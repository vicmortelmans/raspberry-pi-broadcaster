# Raspberry Pi Broadcaster

## Prerequisites:

Nginx must be installed, compiled with the RTMP module. 

Raspberry Pi Broadcaster (RPB) is launched by Nginx, but therefor the Nginx config file must be edited. Mine is in `/usr/local/nginx/conf/nginx.conf`. A sample of my nginx.conf is listed below.

The launch script rpb_server_launch.sh redirects output to syslog, which can be inspected by `journalctl -f | grep RPB`.


## Configuration:

`config.ini` sets the RPB name, website password, camera parameters and destinations. For Youtube destinations, a client secrets file is needed and for Facebook destinations, a long lived token file.

### Youtube client secrets file

Use Google Cloud Console to create a project and activate Youtube Data API v3. Then create oauth 2.0 client ID for Desktop app for scope https://www.googleapis.com/auth/youtube and download client_secrets.json.

## Multiple controllers are included:

- `button_monitor` monitors the button (GPIO21 - pin 40)
- `camera` starts the ffmpeg process that streams from the camera into nginx
- `led_driver` drives the led (GPIO6 - pin 31)
- `ps_monitor` monitors the ffmpeg process that's doing the broadcast
- `ws_server` serves the webpage and manages websocket connections for one or more users

## Allow script to halt the raspberry pi

Check the comments in halt.py for the configuration needed to allow the script to halt the raspberry pi.

## Bugs

- youtube negotiations fail for test account

## Feature requests

- when opening webpage while broadcasting, no links to broadcasts are available
