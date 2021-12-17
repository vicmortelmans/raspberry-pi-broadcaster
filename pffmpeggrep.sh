#!/bin/bash
# used by ps_monitor.py to see if the ffmpeg process is still alive that does the broadcast
# and that is started by start_broadcast.py
ps -ef | grep -E "ffmpeg.*:1936" | grep -v grep

# for debugging without launching ffmpeg, run 'cat /dev/zero' and swith following line on:
#ps -ef | grep -E "zero" | grep -v grep
