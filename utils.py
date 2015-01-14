import json
import requests
import time


def get_top_channels(n):
    twitch_api_url = 'https://api.twitch.tv/kraken/streams/?limit=%i' % n
    streams = json.loads(requests.get(twitch_api_url).text)['streams']
    return [stream['channel']['name'] for stream in streams]


def current_time_in_milli():
    return int(round(time.time() * 1000))
