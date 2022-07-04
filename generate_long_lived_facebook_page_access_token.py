#!/usr/bin/python3
import json
import urllib.parse, urllib.request

short_lived_user_access_token = input("Short-lived user access token: ")
app_id = input("App ID: ")
app_secret = input("App secret: ")

# build the URL for the API endpoint
host = "https://graph.facebook.com"
version = "/v9.0"
path = "/oauth/access_token"
params = urllib.parse.urlencode({
    "grant_type": "fb_exchange_token",
    "client_id": app_id,
    "client_secret": app_secret,
    "fb_exchange_token": short_lived_user_access_token})

url = "{host}{version}{path}?{params}".format(host=host, version=version, path=path, params=
params)
                                             
# open the URL and read the response         
resp = urllib.request.urlopen(url).read()    
                                             
# convert the returned JSON string to a Python datatype 
me = json.loads(resp)
long_lived_user_access_token = me['access_token']

# build the URL for requesting the long-lived page access token
path = "/me/accounts"
params = urllib.parse.urlencode({
    "access_token": long_lived_user_access_token})

url = "{host}{version}{path}?{params}".format(host=host, version=version, path=path, params=params)

# open the URL and read the response
resp = urllib.request.urlopen(url).read()

# write the output to a json file
with open('facebook-test.json', 'w') as outfile:
    json.dump(json.loads(resp), outfile, indent=4)

