import configuration
import create_youtube_broadcast
import create_facebook_broadcast
from async_wrap import async_wrap
import configuration
import logging
from rpb_server import state_machine


@async_wrap
def async_start(title, description):
    # 1. read config for available targets
    # 2. negotiate with youtube and facebook for rtmp addresses
    # 3. start the streams
    # 4. give the 'started' event
    inis = configuration.data.sections()
    rtmps = []  # list of dicts 
    for ini in inis:
        if configuration.data[ini]['type'] == 'youtube':
            logging.info(f"Negotiating with youtube for '{ini}'")
            rtmps.append(create_youtube_broadcast.create_broadcast(ini, title, description).update({'ini':ini}))
        elif configuration.data[ini]['type'] == 'facebook':
            logging.info(f"Negotiating with facebook for '{ini}'")
            rtmps.append(create_facebook_broadcast.create_broadcast(ini, title, description).update({'ini':ini}))
    command = f"{ffmpeg} -f flv -listen 1 -i rtmp://127.0.0.1:1936/webcam/"
    for rtmp in rtmps:
        if 'rtmp' in rtmp:
            ffmpeg = configuration[rtmp['ini'], 'ffmpeg_path']
            command += f"{ffmpeg} -c copy -f flv '{stream['rtmp']}'"
    logging.info(f"Launching stream: {command}")
    # os.system("daemon --stdout=daemon.info --stderr=daemon.err -- %s" % command)
    state_machine.on_event({'name': 'started'})

