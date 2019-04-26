import sys
import json
import logging
import os
import pandas as pd 
import zmq
import datetime


# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

# Connect to tcp ports for pricing/news and different sources 
# Each message send will have a topic indicating the pricing source and then the actual content 
socket.connect ('tcp://127.0.0.1:7000')
socket.setsockopt_string(zmq.SUBSCRIBE, 'IEX')
socket.setsockopt_string(zmq.SUBSCRIBE, 'TrueFX')

poller=zmq.Poller()
poller.register(socket, zmq.POLLIN)
print('Register poller')

# TrueFX 

TrueFXheader=None
TrueFXnames=['Symbol', 'Date', 'Bid', 'Bid_point','Ask', 'Ask_point', 'High', 'Low', 'Open']

def bytes2df(bytestream,header,names):
    data_io = pd.compat.StringIO(bytestream.decode())
    df = pd.read_csv(data_io,header=header,names=names)
    del data_io
    return df 


def ondata(pricingsource,tickdata):
    if pricingsource=='IEX':
        try:
            d = json.loads(message[1])
            print(d)
        except json.decoder.JSONDecodeError:
            print('Not decoded')
    if pricingsource=='TrueFX':
        try:
            df = bytes2df(message[1],TrueFXheader,TrueFXnames)
            df['Date'] = pd.to_datetime(df['Date'], unit='ms')
            df.set_index('Symbol',inplace=True)
            print(df.to_dict())
        except:
            print('Not decoded') 

if __name__=='__main__':
    while True:
        socks = dict(poller.poll(1000))
        if not socks:
            continue    
        if socks[socket] == zmq.POLLIN:
            message = socket.recv_multipart()
            pricingsource=message[0].decode()
            tick=message[1]
            ondata(pricingsource,tick)
