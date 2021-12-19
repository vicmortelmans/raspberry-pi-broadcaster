import configuration
from async_wrap import async_wrap
import configuration
import logging
import os
import shutil
import state


@async_wrap
def start_stream_async():
    ffmpeg = shutil.which("ffmpeg")
    try:
        ffmpeg = configuration.data['DEFAULT']['ffmpeg_path']
    except KeyError as e:
        logging.error(f"Configuration file is missing 'ffmpeg_path' in [DEFAULT] section - using ffmpeg in path {ffmpeg}.")
    brightness = 50
    try:
        brightness = configuration.data['DEFAULT']['brightness']
    except KeyError as e:
        logging.warning(f"Configuration file is missing 'brightness' in [DEFAULT] section - using default of {brightness}.")
    contrast = -10
    try:
        contrast = configuration.data['DEFAULT']['contrast']
    except KeyError as e:
        logging.warning(f"Configuration file is missing 'contrast' in [DEFAULT] section - using default of {contrast}.")
    command_1 = f"v4l2-ctl --set-ctrl video_bitrate=3000000,brightness={brightness},contrast={contrast},sharpness=10"
    logging.info(f"Camera setup command: '{command_1}'")
    os.system(command_1)
    command_2 = f"{ffmpeg} -f v4l2 -framerate 30 -video_size 1920x1080 -input_format h264 -i /dev/video0 -f alsa -ac 2 -i hw:2 -codec:v copy -codec:a aac -b:a 128k -ar 44100 -strict experimental -f flv \"rtmp://localhost:1935/webcam/hhart\""
    logging.info(f"Camera start stream command: '{command_2}'")
    os.system("daemon --stdout=daemon.info --stderr=daemon.err -- %s" % command_2)
    return 
