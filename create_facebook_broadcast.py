#!/usr/bin/python3
import configuration
import json
import logging
import requests
import sys
import urllib.parse, urllib.request, urllib.error


# Full format of the resp dict:

# {
#     "id": "695704821087931",
#     "stream_url": "rtmps://live-api-s.facebook.com:443/rtmp/695704821087931?s_bl=1&s_psm=1&s_sc=695704851087928&s_sw=0&s_vt=api-s&a=AbyDW0etOUDONKEO",
#     "secure_stream_url": "rtmps://live-api-s.facebook.com:443/rtmp/695704821087931?s_bl=1&s_psm=1&s_sc=695704851087928&s_sw=0&s_vt=api-s&a=AbyDW0etOUDONKEO",
#     "stream_secondary_urls": [],
#     "secure_stream_secondary_urls": []
# }


def create_broadcast(ini, title, description):
  # ini is the name as in the section header of the config.ini file
  # title and description can be left empty, in which case the defaults
  # are taken from config.ini

    if not title:
        title = configuration.data[ini]['title']
    if not description:
        description = configuration.data[ini]['description']

    page_name = configuration.data[ini]['name']

    token_file = configuration.data[ini]['long_lived_token']

    # get long-lived Facebook page access token
    with open(token_file) as json_file:
        data = json.load(json_file)
    long_lived_page_access_token = ""
    for page in data["data"]:
        if page["name"] == page_name:
            long_lived_page_access_token = page["access_token"]
            break
    else:
        logging.error(f"The page name is not found in '{token_file}'")
        return {}

    # build the URL for the API endpoint
    host = "https://graph.facebook.com"
    version = "/v19.0"
    path = "/me/live_videos"
    params = {
        "status": "LIVE_NOW",
        "title": title,
        "description": description,
        "access_token": long_lived_page_access_token}

    url = "{host}{version}{path}".format(host=host, version=version, path=path)

    logging.info("Requesting for " + url + " " + json.dumps(params))

    # open the URL and read the response
    try:
        resp = json.loads(requests.post(url, params=params).text)
    except urllib.error.HTTPError as e:
        logging.error("Request failed because of " + e.reason)
        return {}

    logging.info("Success creating facebook broadcast")

    return {
        "id" : resp['id'],
        "rtmp" : resp['stream_url']
    }


if __name__ == "__main__":
    # very crude standalone implementation, expecting as first argument the
    # name as in the section header in the config.ini file, for testing only
    # example: python3 create_broadcast.py "<name as in config.ini header>"
    return_dict = create_broadcast(sys.argv[1], '', '')
    print(json.dumps(return_dict, indent=4))
