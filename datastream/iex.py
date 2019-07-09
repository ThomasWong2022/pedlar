import os
import datetime
import csv
import time
import json

import zmq
import requests



# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect('tcp://127.0.0.1:3000')

import pandas as pd
pd.set_option('expand_frame_repr', False)
pd.set_option('max_columns', 8)

from datetime import timedelta
from pandas.io.common import urlencode
import pandas.compat as compat



def _send_request(session, params):
    base_url = "http://webrates.truefx.com/rates"
    endpoint = "/connect.html"
    url = base_url + endpoint
    s_url = url + '?' + urlencode(params)
    response = session.get(url, params=params)
    return(response)

def read_tick(tickers):
    baseurl = 'https://api.iextrading.com/1.0/tops?symbols='
    tickerstring = ','.join(tickers)
    response = requests.get(baseurl+tickerstring)
    return response.json()


if __name__=='__main__':
    while True:
        tickers = ['SPY','QQQ']
        data = read_tick(tickers)
        for d in data:
            t = json.dumps(d)
            socket.send_multipart([bytes('IEX','utf-8'), bytes(t,'utf-8')])
            print(t)
        time.sleep(0.01)
