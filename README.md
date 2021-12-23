# Raspberry Pi Broadcaster

## Prerequisites:

Nginx must be installed, compiled with the RTMP module. 

Raspberry Pi Broadcaster (RPB) is launched by Nginx, but therefor the Nginx config file must be edited. Mine is in `/usr/local/nginx/conf/nginx.conf`. A sample of my nginx.conf is listed below.

The launch script rpb_server_launch.sh redirects output to syslog, which can be inspected by `journalctl -f | grep RPB`.


## Configuration:

`config.ini` sets the RPB name, website password, camera parameters and destinations. For Youtube destinations, a client secrets file is needed and for Facebook destinations, a long lived token file.

### Youtube client secrets file and token files

Use Google Cloud Console to create a project and activate Youtube Data API v3. Then create oauth 2.0 client ID for Desktop app for scope https://www.googleapis.com/auth/youtube and download client_secrets.json.

Youtube also requires a token file for each destination. To create this, run `python3 create_youtube_broadcast.py <destination>` where <destination> is the header name of the target in `config.ini`. You'll get an URL to go to for authentication and if that is successful, a new file `youtube-<destination>.json` is available in this directory. If you have multiple youtube accounts or brand accounts, make sure to select the correct one during authentication, otherwise a token will be created, but the streaming will still fail. There may be an expiry date on this token, at which point these steps can be repeated.

### Allow script to halt the raspberry pi

Check the comments in halt.py for the configuration needed to allow the script to halt the raspberry pi.


## Multiple controllers are included:

- `button_monitor` monitors the button (GPIO21 - pin 40)
- `camera` starts the ffmpeg process that streams from the camera into nginx
- `led_driver` drives the led (GPIO6 - pin 31)
- `ps_monitor` monitors the ffmpeg process that's doing the broadcast
- `ws_server` serves the webpage and manages websocket connections for one or more users

## State

State is managed in `state.py`. When events come in via the controllers, actions that accompany the state change are defined inside this module.

## Bugs

- youtube negotiations fail for test account

## Feature requests

- when opening webpage while broadcasting, no links to broadcasts are available


## Sample nginx.conf

```
user  pi pi;
worker_processes  auto;

error_log  syslog:server=unix:/dev/log,tag=nginx,nohostname,severity=info;

events {
    worker_connections  1024;
}

rtmp {
    server {
        exec_static /home/pi/raspberry-pi-broadcaster/rpb_server_launch.sh;
        listen 1935;
        chunk_size 4000;
        
        application webcam {
            live on;
            hls on;
            hls_path /tmp/webcam;
	    hls_fragment 3;
            hls_playlist_length 60;
            deny play all;
            push rtmp://127.0.0.1:1936/webcam/;
        }
    }
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    access_log syslog:server=unix:/dev/log,tag=nginx,nohostname,severity=info combined;

    sendfile        on;

    keepalive_timeout  65;

    server {
        listen 80;

        server_name  localhost livestream.jezus-hart.be;

        if ($scheme != "https") {
            return 301 https://$host$request_uri;
        } 
    }

    server {
        listen 443 ssl; 

        server_name  livestream.jezus-hart.be;

        location /webcam {
            add_header 'Cache-Control' 'no-cache';
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Expose-Headers' 'Content-Length';

            if ($request_method = 'OPTIONS') {
                add_header 'Access-Control-Allow-Origin' '*';
                add_header 'Access-Control-Max-Age' 1728000;
                add_header 'Content-Type' 'text/plain charset=UTF-8';
                add_header 'Content-Length' 0;
                return 204;
            }

            types {
                application/dash+xml mpd;
                application/vnd.apple.mpegurl m3u8;
                video/mp2t ts;
            }

            root /tmp/;
        }

        location / {
            proxy_pass "http://localhost:8080/";
        }

        location /socket.io/ {
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_pass "http://localhost:8080/socket.io";
            proxy_read_timeout 1d;
            proxy_send_timeout 1d;
            proxy_connect_timeout 1d;
        }

        ssl_certificate /etc/letsencrypt/live/livestream.jezus-hart.be/fullchain.pem; 
        ssl_certificate_key /etc/letsencrypt/live/livestream.jezus-hart.be/privkey.pem; 
        ssl_session_cache shared:le_nginx_SSL:1m;
        ssl_session_timeout 1440m;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
        ssl_prefer_server_ciphers on;

        ssl_ciphers "ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES256-SHA:ECDHE-ECDSA-DES-CBC3-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA:!DSS";

    }
}
```
