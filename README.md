# Raspberry Pi Broadcaster

## Prerequisites:

Nginx must be installed, compiled with the RTMP module. 

Raspberry Pi Broadcaster (RPB) is launched by Nginx, but therefor the Nginx config file must be edited. Mine is in `/usr/local/nginx/conf/nginx.conf`. A sample of my nginx.conf is listed below.

The launch script rpb_server_launch.sh redirects output to syslog, which can be inspected by `journalctl -f | grep RPB`.


## Configuration:

- `config.ini` sets the RPB name, website password, camera parameters and destinations. For Youtube destinations, a client secrets file is needed and for Facebook destinations, a long lived token file.

- Youtube requires a token file for each destination. To create this, run `python3 create_youtube_broadcast.py <destination>` where <destination> is the header name of the target in `config.ini`. You'll get an URL to go to for authentication and if that is successful, a new file `youtube-<destination>.json` is available in this directory. If you have multiple youtube accounts or brand accounts, make sure to select the correct one during authentication, otherwise a token will be created, but the streaming will still fail. There may be an expiry date on this token, at which point these steps can be repeated.

To start the RPB, run `./rpb_server.py` or `python3 rpb_server.py`.

## Multiple controllers are included:

- `button_monitor` monitors the button (GPIO21 - pin 40)
- `camera` starts the ffmpeg process that streams from the camera into nginx
- `led_driver` drives the led (GPIO6 - pin 31)
- `ps_monitor` monitors the ffmpeg process that's doing the broadcast
- `ws_server` serves the webpage and manages websocket connections for one or more users

In a final setup, this script will be started from the NGINX service. 

## Allow script to halt the raspberry pi

Check the comments in halt.py for the configuration needed to allow the script to halt the raspberry pi.

## Bugs

- youtube negotiations fail for test account

## Feature requests

- when opening webpage while broadcasting, no links to broadcasts are available
