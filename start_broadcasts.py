import configuration
import create_youtube_broadcast
import create_facebook_broadcast
from async_wrap import async_wrap
import configuration
import logging
import os
import ps_monitor
import state
import subprocess
import traceback


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
            try:
                rtmp = create_youtube_broadcast.create_broadcast(ini, title, description)
                rtmp.update({'ini':ini})
                rtmp.update({'view':configuration.data[ini]['view']})  # for reporting in return event
                rtmps.append(rtmp)
            except Exception as e:
                logging.error(f"Youtube negotiations failes for '{ini}', see traceback:", exc_info=True)
                #logging.error(traceback.format_exc())
        elif configuration.data[ini]['type'] == 'facebook':
            logging.info(f"Negotiating with facebook for '{ini}'")
            try:
                rtmp = create_facebook_broadcast.create_broadcast(ini, title, description)
                rtmp.update({'ini':ini})
                rtmp.update({'view':configuration.data[ini]['view']})  # for reporting in return event
                rtmps.append(rtmp)
            except Exception as e:
                logging.error(f"Facebook negotiations failes for '{ini}', see traceback:", exc_info=True)
                #logging.error(traceback.format_exc())
    logging.info(f"Result of negotiations is {len(rtmps)} targets:")
    logging.info(str(rtmps))
    try:
        ffmpeg = configuration.data['DEFAULT']['ffmpeg_path']
    except KeyError as e:
        logging.error("Configuration file is missing 'ffmpeg_path' in [DEFAULT] section.")
    command = f"{ffmpeg} -f flv -listen 1 -i rtmp://127.0.0.1:1936/webcam/"
    for rtmp in rtmps:
        if 'rtmp' in rtmp:
            command += f" -c copy -f flv '{rtmp['rtmp']}'"
    logging.info(f"Launching stream: {command}")
    os.system("daemon --stdout=daemon.info --stderr=daemon.err -- %s" % command)
    # return the new state
    return {'name': 'started', 'data': rtmps}

@async_wrap
def async_stop():
    pid = ps_monitor.pid
    subprocess.getoutput('kill ' + pid)    
    logging.info(f"Killed process {str(pid)}")
    return {'name': 'stopped'}
