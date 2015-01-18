import json
import requests
import time

from requests.exceptions import ConnectionError, SSLError

def get_top_streams(n):
    twitch_api_url = 'https://api.twitch.tv/kraken/streams/?limit=%i' % n
    try:
        return json.loads(requests.get(twitch_api_url).text)['streams']
    except (ValueError, ConnectionError, SSLError):
        time.sleep(5)
        return get_top_streams(n)


def get_channel_names(streams):
    return [stream['channel']['name'] for stream in streams]


def current_time_in_milli():
    return int(round(time.time() * 1000))
