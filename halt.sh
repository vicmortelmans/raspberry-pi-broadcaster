#!/bin/sh
# this script only works after running `visudo` and adding this line:
# pi ALL=(ALL) NOPASSWD: /sbin/poweroff, /sbin/reboot, /sbin/shutdown
sudo shutdown -r
