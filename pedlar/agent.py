
import argparse
from collections import OrderDict, namedtuple
from datetime import datetime
import logging
import re
import struct

import json
import pandas as pd
import numpy as np

import requests




# Datafeed functions 
import truefx

logger = logging.getLogger(__name__)

# pylint: disable=broad-except,too-many-instance-attributes,too-many-arguments

Holding =  ['exchange', 'ticker', 'volume']
Order =  ['id', 'exchange', 'ticker', 'price', 'volume', 'type']
Trade = ['id', 'exchange', 'ticker', 'entryprice', 'exitprice', 'volume']
Tick = ['time', 'exchange', 'ticker', 'bid', 'ask', 'bidsize', 'asksize']
Book = ['exchange', 'ticker', 'bid', 'ask', 'bidsize', 'asksize']


class Agent:
    """Base class for Pedlar trading agent."""

    time_format = "%Y.%m.%d %H:%M:%S" # datetime column format

    def __init__(self, username="nobody", truefxid='', truefxpassword='', pedlarurl='localhost:5000', maxsteps=10000):
        
        self.endpoint = pedlarurl
        self.username = username # pedlarweb username for mongodb collection 
        self.maxsteps = maxsteps

        self.orders = pd.DataFrame(columns=Order).set_index('id')
        self.trades = pd.DataFrame(columns=Trade).set_index('id')
        self.portfolio = pd.DataFrame(columns=Holding) 
        self.history = pd.DataFrame(columns=Tick).set_index(['time','exchange','ticker'])
        self.orderbook = pd.DataFrame(columns=Book).set_index(['exchange','ticker'])
        self.balance = 0 # PnL 
        
        self.orderid = 0 
        self.tradeid = 0
        self.tradesession = np.random.randint(1,1000000)


    @classmethod
    def from_args(cls, parents=None):
        """Create agent instance from command line arguments."""
        parser = argparse.ArgumentParser(description="Pedlar trading agent.",
                                                                         fromfile_prefix_chars='@',
                                                                         parents=parents or list())
        parser.add_argument("-u", "--username", default="nobody", help="Pedlar Web username.")
        parser.add_argument("-t", "--truefxid", default="", help="Username for Truefx")
        parser.add_argument("-p", "--truefxpassword", default="", help="Truefc password.")
        parser.add_argument("-m", "--pedlarurl", default="", help="Algosoc Server")
        return cls(**vars(parser.parse_args()))


    def start_agent(self):
        # create user profile in MongoDB if not exist 
        payload = {'User':self.username}
        r = requests.post(self.endpoint+"/user", data=payload, allow_redirects=False)
        data = json.load(r)
        if data['exist']:
            print('Existing user {} found'.format(data['user'])
        # create truefx session 
        session, session_data, flag_parse_data, authrorized = truefx.config(api_format ='csv', flag_parse_data = True)
        self.truefxsession = session
        self.truefxsession_data = session_data
        self.truefxparse = flag_parse_data
        self.truefxauthorized = authrorized
        # connect to other datasource 
        self.step = 0
        return None 

    def save_record(self):
        timestamp = datetime.now().strftime(time_format)
        pricefilename = 'Historical_Price_{}_{}.csv'.format(self.username, timestamp)
        tradefilename = 'Trade_Record_{}_{}.csv'.format(self.username, timestamp)
        # save price history 
        # save trade record 
        return None 

    def universe_definition(self, tickerlist=None):
        if tickerlist is None:
            tickerlist = [('TrueFX','GBP/USD'), ('TrueFX','EUR/USD')]
        self.portfolio.set_index(pd.MultiIndex.from_tuples(tickerlist, names=('exchange', 'ticker')))
        return None 

    def download_tick(self):

        truefxdata = truefx.read_tick(self.truefxsession, self.truefxsession_data, self.truefxparse, self.truefxauthorized) 

    def update_history


    def run_agents(self):


    