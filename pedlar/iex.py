import os
import datetime
import csv
import time
import json 

import requests

import pandas as pd
import numpy as np

iexbaseurl = 'https://api.iextrading.com/1.0'

def get_TOPS(tickerstring):
    iextopsurl = iexbaseurl + '/tops?symbols='
    query = iextopsurl + tickerstring
    query = 'https://api.iextrading.com/1.0/hist?date=20190515'
    r = requests.get(query)
    data = r.json()
    snapshot = pd.DataFrame(data)
    snapshot['exchange'] = 'IEX'
    snapshot.rename(columns={"symbol": "ticker", "bidPrice": "bid", 'askPrice':'ask', 'bidSize':'bidsize', 'askSize':'asksize', 'lastUpdated':'time'})
    snapshot['time'] = pd.to_datetime(snapshot['time'], unit='us')  
    columns = ['time', 'exchange', 'ticker', 'bid', 'ask', 'bidsize', 'asksize']
    return snapshot[columns] 

if __name__=='__main__':
    get_TOPS('FB,APPL')

