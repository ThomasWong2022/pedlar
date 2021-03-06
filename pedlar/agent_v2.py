
import argparse
from collections import namedtuple
from datetime import datetime
import logging
import re
import struct
import time

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
Order =  ['order_id', 'exchange', 'ticker', 'price', 'volume', 'type', 'time']
Trade = ['trade_id', 'exchange', 'ticker', 'entryprice', 'exitprice', 'volume', 'entrytime', 'exittime']
Tick = ['time', 'exchange', 'ticker', 'bid', 'ask', 'bidsize', 'asksize']
Book = ['exchange', 'ticker', 'bid', 'ask', 'bidsize', 'asksize', 'time']


class Agent:
    """Base class for Pedlar trading agent."""

    

    def __init__(self, maxsteps=100, universefunc=None, ondatafunc=None, ondataparams=None,
    username="nobody", truefxid='', truefxpassword='', pedlarurl='http://127.0.0.1:5000'):
        
        self.endpoint = pedlarurl
        self.username = username  
        self.maxsteps = maxsteps

        self.orders = pd.DataFrame(columns=Order).set_index('order_id')
        self.trades = pd.DataFrame(columns=Trade).set_index('trade_id')
        
        self.history = pd.DataFrame(columns=Tick).set_index(['time', 'exchange', 'ticker'])
        self.orderbook = pd.DataFrame(columns=Book).set_index(['exchange', 'ticker'])
        self.balance = 0 # PnL 

        self.holdings = []

        # caplim is the max amount of capital allocated 
        # shorting uses up caplim but gives cash 
        # check caplim at each portfolio rebalance and scale down the target holding if that exceeds caplim
         
        self.portfoval = 50000
        self.pnl = 0
        self.cash = 50000
        self.caplim = self.portfoval * 2
        
        self.orderid = 0 
        self.tradeid = 0
        self.tradesession = 0

        # User defined functions 
        self.universe_definition = universefunc
        self.ondata = ondatafunc
        self.ondatauserparms = ondataparams

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
        try:
            payload = {'user':self.username}
            r = requests.post(self.endpoint+"/user", json=payload)
            data = r.json()
            if data['exist']:
                print('Existing user {} found'.format(data['username']))
            self.username = data['username']
            self.connection = True
            self.tradesession = data['tradesession']
        except:
            self.connection = False
        # create truefx session 
        session, session_data, flag_parse_data, authrorize = truefx.config(api_format ='csv', flag_parse_data = True)
        self.truefxsession = session
        self.truefxsession_data = session_data
        self.truefxparse = flag_parse_data
        self.truefxauthorized = authrorize
        # connect to other datasource 
        # set up trading universe
        self.step = 0
        if self.universe_definition:
            self.universe = self.universe_definition()
        else:
            self.universe = None 
        self.create_portfolio(self.universe,verbose)
        return None

    def save_record(self):
        # upload to pedlar server 
        if self.connection:
            payload = {'user_id':self.username,'pnl':self.balance}
            r = requests.post(self.endpoint+"/tradesession", json=payload)
            self.tradesession = r.json()['tradesession']
        time_format = "%Y_%m_%d_%H_%M_%S" # datetime column format
        timestamp = datetime.now().strftime(time_format)
        pricefilename = 'Historical_Price_{}.csv'.format(self.tradesession)
        tradefilename = 'Trade_Record_{}.csv'.format(self.tradesession)
        # save price history 
        self.history.to_csv(pricefilename)
        self.history_trades = pd.concat(self.holdings,axis=0)
        self.history_trades.to_csv(tradefilename)
        # upload trades for a tradesession 
        if self.connection and False:
            self.trades['backtest_id'] = self.tradesession
            self.trades['entrytime'] = self.trades['entrytime'].astype(np.int64)/1000000
            self.trades['exittime'] = self.trades['exittime'].astype(np.int64)/1000000
            self.trades.reset_index(inplace=True)
            trades = self.trades.to_dict(orient='record')
            for t in trades:
                r = requests.post(self.endpoint+'/trade', json=t)
        return None 

    def create_portfolio(self, tickerlist=None, verbose=False):

        if tickerlist is None:
            tickerlist = [('TrueFX','GBP/USD'), ('TrueFX','EUR/USD'), ('IEX','SPY'), ('IEX','QQQ')]

        self.portfolio = pd.DataFrame(columns=['volume'], index=pd.MultiIndex.from_tuples(tickerlist, names=('exchange', 'ticker'))) 
        self.portfolio['volume'] = 0

        iextickers = [x[1] for x in tickerlist if x[0]=='IEX']
        self.iextickernames = ','.join(iextickers)
        if self.iextickernames == '':
            self.iextickernames = 'SPY,QQQ'

        if verbose:
            print('Portfolio')
            print(self.portfolio)

        self.tickers = tickerlist
        self.n_assets = len(self.tickers)

        return None 

    def download_tick(self):
        # implement methods to get price data in dataframes 
        truefxdata = truefx.read_tick(self.truefxsession, self.truefxsession_data, self.truefxparse, self.truefxauthorized) 
        iexdata = iex.get_TOPS(self.iextickernames)
        return truefxdata, iexdata

    def update_history(self, verbose=False):
        # get raw data 
        truefx, iex = self.download_tick()
        self.historysize = truefx.shape[0] + iex.shape[0]

        # build order book 
        self.orderbook = pd.DataFrame(columns=Book).set_index(['exchange', 'ticker'])
        self.orderbook = self.orderbook.append(truefx.set_index(['exchange', 'ticker']))
        self.orderbook = self.orderbook.append(iex.set_index(['exchange', 'ticker']))
        self.orderbook['mid'] = (self.orderbook['ask'] + self.orderbook['bid'])/2

        # update price history 
        self.history = self.history.append(truefx.set_index(['time', 'exchange', 'ticker']))
        self.history = self.history.append(iex.set_index(['time', 'exchange', 'ticker']))

        # Ensure uniquess in price history
        self.history = self.history[~self.history.index.duplicated(keep='first')]

        # Remove old data in price history
        self.maxlookup = 5
        self.history = self.history.iloc[-self.maxlookup*self.historysize:,:]
         

        if verbose:
            print('Price History')
            print(self.history)
            print('Orderbook')
            print(self.orderbook)

    def rebalance(self, new_weights, verbose=False):
        """
        Input: new_weights: dataframe with same index as portfolio
        """
        # add historical holdings
        now = datetime.now()
        current_holdings = self.portfolio.transpose().set_index(np.array([now]))
        current_holdings['PorftolioValue'] = self.portfoval
        self.holdings.append(current_holdings)
        # construct changes 
        self.holdings_change = new_weights - self.portfolio
        # perform orders wrt to cash 
        # check asset allocation limit 
        self.portfoval = np.sum(self.portfolio['volume'] * self.orderbook['mid']) + self.cash
        self.caplim = self.portfoval * 2
        self.abspos = np.sum(np.abs(new_weights['volume']) * self.orderbook['mid']) + self.cash
        if self.abspos > self.caplim:
            raise ValueError('Portfolio allocation cannot exceed capital limit')
        # update to target portfolio
        # check cash must be positive 
        self.holdings_change['transact'] = np.where(self.holdings_change['volume']>0, self.orderbook.loc[self.holdings_change.index,:]['ask'],self.orderbook.loc[self.holdings_change.index,:]['bid']) * self.holdings_change['volume']
        self.cash = self.cash - np.sum(self.holdings_change['transact'])
        if self.cash < 0:
            raise ValueError('Cash cannot be negative')
        self.portfolio = new_weights
        return None 



    def run_agents(self, verbose=False):

        self.start_agent(verbose)
        
        if verbose:
            print(self.portfolio)

        # starting portfolio with zero holding 
        new_weights = self.portfolio

        while self.step < self.maxsteps:
            self.update_history(False)
            self.rebalance(new_weights)
            # Run user provided function to get target portfolio weights for the next data
            if not self.ondatauserparms:
                self.ondatauserparms = {}
            new_weights = self.ondata(step=self.step, history=self.history, portfolio=self.portfolio, trades=self.trades, caplim=self.caplim, **self.ondatauserparms)
            self.portfoval = np.sum(self.portfolio['volume'] * self.orderbook['ask']) + self.cash
            self.step += 1
            time.sleep(1)
            if verbose:
                print('Step {} {}'.format(self.step, self.portfoval))
                print()
                print('Portfolio')
                print(self.portfolio)
                print()
        
        self.save_record()

if __name__=='__main__':

    def ondata(step, history, portfolio, trades, caplim):
        target_portfolio = portfolio.copy()
        # calculate target portfolio which is random for this example
        target_portfolio['volume'] = (np.random.random() - 0.5) * 100
        return target_portfolio

    agent = Agent(ondatafunc=ondata)
    agent.run_agents(verbose=True)


            




    