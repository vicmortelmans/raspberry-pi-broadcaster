# Raspberry Pi Broadcaster

Configuration:

- `config.ini` sets the RPB name, website password, camera parameters and destinations. For Youtube destinations, a client secrets file is needed and for Facebook destinations, a long lived token file.

To start the RPB, run `rpb_server.py` or `python3 rpb_server.py`.

Multiple controllers are included:

- `button_monitor` monitors the button (GPIO21 - pin 40)
- `led_driver` drives the led (GPIO6 - pin 31)
- `ps_monitor` monitors the ffmpeg process that's doing the broadcast
- `ws_server` serves the webpage and manages websocket connections for one or more users

In a final setup, this script will be started from the NGINX service. 


Bugs

- website start streaming not working because websocket closed (only after starting preview stream?)
- youtube negotiations fail for test account
- button stop not working
- reboot not implemented
- website stop not working when opened while broadcasting


Feature requests

- when opening webpage while broadcasting, no links to broadcasts are available
