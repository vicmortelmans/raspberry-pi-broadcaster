import httplib2
import os
import sys
import datetime, time
import logging
import json
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import google.auth.transport.requests
import google.oauth2.credentials
import requests
import configuration
from slugify import slugify

# The client secrets file contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Cloud Console at https://cloud.google.com/console.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def get_authenticated_service(name):
    client_secrets_file = configuration.data[name]['client_secrets']
    credentials = None
    credentials_json_file = "youtube-%s.json" % slugify(name)
    if os.path.exists(credentials_json_file):
        # load credentials from file
        with open(credentials_json_file, encoding='utf-8') as f:
            credentials_json = json.load(f)
        credentials = google.oauth2.credentials.Credentials.from_authorized_user_info(credentials_json)
    if not credentials or not credentials.valid:
        # no credentials file or invalid credentials
        if credentials and credentials.expired and credentials.refresh_token:
            # refresh
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
        else:
            # re-authenticate
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, [YOUTUBE_READ_WRITE_SCOPE])
            credentials = flow.run_console()
        # save credentials to file
        credentials_json = credentials.to_json()
        with open(credentials_json_file, 'w', encoding='utf-8') as f:
            f.write(credentials_json)
    return googleapiclient.discovery.build(
        YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)


# Create a liveBroadcast resource and set its title, scheduled start time,
# scheduled end time, and privacy status.
def insert_broadcast(youtube, title, description, start_time, end_time):
  # https://developers.google.com/youtube/v3/live/docs/liveBroadcasts/insert
  # https://developers.google.com/youtube/v3/live/docs/liveBroadcasts#resource
  insert_broadcast_response = youtube.liveBroadcasts().insert(
    part="snippet,status,contentDetails",
    body=dict(
      snippet=dict(
        title=title,
        description=description,
        scheduledStartTime=start_time,
        scheduledEndTime=end_time
      ),
      status=dict(
        privacyStatus="public"
      ),
      contentDetails=dict(
        enableAutoStart=True,
        enableAutoStop=True
      )
    )
  ).execute()

  snippet = insert_broadcast_response["snippet"]

  logging.info("Broadcast '%s' with title '%s' was published at '%s'." % (
    insert_broadcast_response["id"], snippet["title"], snippet["publishedAt"]))
  return {
    "id" : insert_broadcast_response["id"]
  }

# Create a liveStream resource and set its title, format, and ingestion type.
# This resource describes the content that you are transmitting to YouTube.
def insert_stream(youtube, title):
  # https://developers.google.com/youtube/v3/live/docs/liveStreams/insert
  # https://developers.google.com/youtube/v3/live/docs/liveStreams#resource
  insert_stream_response = youtube.liveStreams().insert(
    part="snippet,cdn",
    body=dict(
      snippet=dict(
        title=title
      ),
      cdn=dict(
        frameRate="variable",
        ingestionType="rtmp",
        resolution="variable"
      )
    )
  ).execute()

  snippet = insert_stream_response["snippet"]
  rtmp = insert_stream_response["cdn"]["ingestionInfo"]

  logging.info("Stream '%s' with title '%s' was inserted." % (
    insert_stream_response["id"], snippet["title"]))
  return {
    "id" : insert_stream_response["id"],
    "rtmp" : rtmp["ingestionAddress"] + '/' + rtmp["streamName"]
  }


# Bind the broadcast to the video stream. By doing so, you link the video that
# you will transmit to YouTube to the broadcast that the video is for.
def bind_broadcast(youtube, broadcast_id, stream_id):
  bind_broadcast_response = youtube.liveBroadcasts().bind(
    part="id,contentDetails",
    id=broadcast_id,
    streamId=stream_id
  ).execute()

  logging.info("Broadcast '%s' was bound to stream '%s'." % (
    bind_broadcast_response["id"],
    bind_broadcast_response["contentDetails"]["boundStreamId"]))
  

def create_broadcast(name, title, description):
  # name is as in the section header of the config.ini file
  # title and description can be left empty, in which case the defaults
  # are taken from config.ini

  if not title:
      title = configuration.data['DEFAULT']['title']
  if not description:
      description = configuration.data['DEFAULT']['description']
  t = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
  t2 = (datetime.datetime.utcnow() + datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%SZ')

  youtube = get_authenticated_service(name)
  try:
    broadcast = insert_broadcast(youtube, title, description, t, t2)
    stream = insert_stream(youtube, title)
    bind_broadcast(youtube, broadcast["id"], stream["id"])
    logging.info("Success creating youtube broadcast")
    return {
        "id" : broadcast["id"],
        "rtmp" : stream["rtmp"]
    }
  except googleapiclient.errors.HttpError as e:
    logging.error("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
    return {}


if __name__ == "__main__":
    # very crude standalone implementation, expecting as first argument the
    # name as in the section header in the config.ini file, for testing only
    # example: python3 create_youtube_broadcast.py "<name as in config.ini header>"
    return_dict = create_broadcast(sys.argv[1], '', '')
    print(json.dumps(return_dict, indent=4))
