
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
import iex

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

    def __init__(self, username="nobody", truefxid='', truefxpassword='', pedlarurl='localhost:5000', maxsteps=500, tickers=None):
        
        self.endpoint = pedlarurl
        self.username = username # pedlarweb username for mongodb collection 
        self.tickers = tickers
        self.maxsteps = maxsteps

        self.orders = pd.DataFrame(columns=Order).set_index('id')
        self.trades = pd.DataFrame(columns=Trade).set_index('id')
        
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


    def start_agent(self, verbose=False):
        # create user profile in MongoDB if not exist 
        payload = {'User':self.username}
        r = requests.post(self.endpoint+"/user", data=payload, allow_redirects=False)
        data = r.json()
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
        self.universe_definition(self.tickers, verbose)
        return None 

    def save_record(self):
        timestamp = datetime.now().strftime(time_format)
        pricefilename = 'Historical_Price_{}_{}.csv'.format(self.username, timestamp)
        tradefilename = 'Trade_Record_{}_{}.csv'.format(self.username, timestamp)
        # save price history 
        self.history.to_csv(pricefilename)
        self.trades.to_csv(tradefilename)
        return None 

    def universe_definition(self, tickerlist=None, verbose=False):

        if tickerlist is None:
            tickerlist = [('TrueFX','GBP/USD'), ('TrueFX','EUR/USD')]

        self.portfolio = pd.DataFrame(columns=['volume'], index=pd.MultiIndex.from_tuples(tickerlist, names=('exchange', 'ticker'))) 
        self.portfolio['volume'] = 0

        iextickers = [x[1] for x in tickerlist if x[0]=='IEX']
        self.iextickernames = ','.join(iextickers)

        if verbose:
            print('Portfolio')
            print(self.portfolio)

        return None 

    def download_tick(self):
        # implement methods to get price data in dataframes 
        truefxdata = truefx.read_tick(self.truefxsession, self.truefxsession_data, self.truefxparse, self.truefxauthorized) 
        iexdata = iex.get_TOPS(self.iextickernames)
        return truefxdata, iexdata

    def update_history(self, verbose=False):
        truefx, iex = self.downlad_tick()
        # update price history 
        self.history.append(truefx.set_index(['time','exchange','ticker']))
        self.history.append(iex.set_index(['time','exchange','ticker']))

        # build order book 
        self.orderbook = pd.DataFrame(columns=Book).set_index(['exchange','ticker'])
        self.orderbook.append(truefx.drop('time',axis=1).set_index(['exchange','ticker'])
        self.orderbook.append(iex.drop('time',axis=1).set_index(['exchange','ticker'])

        if verbose:
            print('Price History')
            print(self.history)
            print('Orderbook')
            print(self.orderbook)


    def update_trades(self, verbose=False):
        # check order list 

        return None 

    
    def create_order(self, type='market', volume=1, exchange='TrueFX', ticker='GBP/USD'):

        return None


    def ondata(self, verbose=False):

        # make trade decisions 
        # self.history gives the most recent objects 
        self.create_order(volume=1, exchage='TrueFX', ticker='GBP/USD')

        return None 

    def run_agents(self, verbose=False):

        self.start_agent(verbose)

        while self.step < self.maxsteps:
            self.update_history(verbose)
            self.ondata(verbose)
            self.update_trades(verbose)
            self.step += 1

        self.save_record()

            




    