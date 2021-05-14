import datetime
import json
import requests
import socket

# This file exposes a dict 'defaults' that is picked when rendering the rpb_console 

def get_liturgical_day():
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    url = "https://publication.evangelizo.ws/NL/days/" + date
    try:
        resp = requests.get(url).text
        data = json.loads(resp)
        return data['data']['liturgic_title']
    except:
        return date


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


defaults = {
    'liturgical_day': get_liturgical_day(),
    'ip': get_ip()
}

