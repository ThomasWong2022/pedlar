"""Local execution broker for Flask Broker."""
import argparse
from collections import namedtuple
import struct
import logging
import json 
from eventlet import GreenPool
from eventlet.green import zmq

# Designed to run locally only
if __name__ != "__main__":
  raise RuntimeError("Can only run as stand-alone script.")

# Setup Arguments
logger = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description=__doc__, fromfile_prefix_chars='@')
parser.add_argument("-t", "--ticker", default="tcp://127.0.0.1:7000", help="Ticker URL")
parser.add_argument("-b", "--broker_host", default="tcp://127.0.0.1:7100", help="Broker serve URL")
parser.add_argument("-i", "--order_id", default=1, type=int, help="Initial order id")
parser.add_argument("-l", "--leverage", default=100, type=int, help="Account leverage")
ARGS = parser.parse_args()

# Context are thread safe already,
# we'll create one global one for all sockets
context = zmq.Context()
Order = namedtuple('Order', ['id', 'exchange', 'ticker', 'price', 'volume', 'type'])

# Globals
BID, ASK = 0.0, 0.0
ORDERS = dict() # Orders indexed using order id
MARKET = dict() # Market has the recent BID ASK 

# MARKET dict example {'IEX:SPY:Bid':280,'IEX:SPY:Ask':281,} The idea is that each Key-Value pair 
# is translatable to a Redis Cache 


# Need to define a way to store the latest quotes of a security 


def handle_tick():
  """Listen to incoming tick updates."""
  socket = context.socket(zmq.SUB)
  # Set topic filter, this is a binary prefix
  # to check for each incoming message
  # set from server as uchar topic = X
  # We'll subsribe to only tick updates for now
  socket.setsockopt(zmq.SUBSCRIBE, bytes())
  logger.info("Connecting to ticker: %s", ARGS.ticker)
  socket.connect(ARGS.ticker)
  while True:
    message = socket.recv_multipart()
    pricingsource = message[0].decode()
    tickdata = message[1]
    if pricingsource == 'IEX':
      d = json.loads(tickdata)
      logger.debug("IEX Tick %s", d)
    # To be implemeted later 
    if pricingsource == 'TrueFX':
      pass
    if pricingsource == 'Sample':
      d = json.loads(tickdata)
      global MARKET
      MARKET['Sample:ICL:bid'] = d['bid']
      MARKET['Sample:ICL:ask'] = d['ask'] 
      logger.debug("Sample Tick %s", d)
    # # unpack bytes https://docs.python.org/3/library/struct.html
    # bid, ask = struct.unpack_from('dd', raw, 1) # offset topic
    # logger.debug("Tick: %f %f", bid, ask)
    # # We'll use global to pass tick data between green threads
    # # since only 1 actually run at a time
    # global BID, ASK # pylint: disable=global-statement
    # BID, ASK = bid, ask
  # socket will be cleaned up at garbarge collection

def handle_broker():
  """Listen to incoming broker requests."""
  socket = context.socket(zmq.REP)
  socket.bind(ARGS.broker_host)
  logger.info("Broker listening on: %s", ARGS.broker_host)
  nextid = ARGS.order_id
  while True:
    raw = socket.recv()
    # Prepare request: ulong order_id, double volume, uchar action
    # order_id, volume, action = struct.unpack('LdB', raw)
    # Prepare response: ulong order_id, double price, double profit, uint retcode
    d = json.loads(raw)
    resp = {'order_id':d['order_id'], 'price': 0.0, 'profit': 0.0, 'retcode':1} # Assume failure
    
    if d['action'] == 1 and d['order_id'] in ORDERS: # Close order
      # BIG ASSUMPTION, account currency is the same as base currency
      # Ex. GBP account trading on GBPUSD since we don't have other
      # exchange rates streaming to us to handle conversion
      order = ORDERS.pop(d['order_id'])
      if order.type == 2:
        index = order.exchange + ':' + order.ticker + ':bid'
        closep = MARKET.get(index, 0)
        diff = closep - order.price
      else:
        index = order.exchange + ':' + order.ticker + ':ask'
        closep = MARKET.get(index, 0)
        diff = order.price - closep
      profit = diff*ARGS.leverage*order.volume
      resp = {'order_id':d['order_id'], 'price': closep, 'profit': profit, 'retcode':0}
      logger.info("CLOSING: %s", resp)
    
    elif d['action'] in (2, 3): # Buy - Sell
      if d['action'] == 2:
        index = d['exchange']  + ':' + d['ticker'] + ':ask'
        oprice = MARKET.get(index, 0)
        profit = 0
      else:
        index = d['exchange']  + ':' + d['ticker'] + ':bid'
        oprice = MARKET.get(index, 0)
        profit = 0       
      
      order = Order(id=nextid, exchange=d['exchange'], ticker=d['ticker'], price=oprice, volume=d['volume'], type=d['action'])
      ORDERS[nextid] = order
      logger.info("ORDER: %s", order)
      resp = {'order_id':nextid, 'price': oprice, 'profit': profit, 'retcode':0}
      nextid += 1
    # Unknown action otherwise
    socket.send(bytes(json.dumps(resp), 'utf-8'))

# Spawn green threads
logging.basicConfig(level=logging.INFO)
pool = GreenPool()
try:
  pool.spawn_n(handle_tick)
  pool.spawn_n(handle_broker)
  pool.waitall() # Loops forever
finally:
  # There might some orphan orders left over
  print("ORPHANS:", ORDERS)
