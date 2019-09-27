

# :chart_with_upwards_trend: pedlar
Pedlar is an algorithmic trading platform for Python designed for trading events, competitions and sessions such as Algothons. It uses real time data from IEX and TrueFX. It aims to support trading multiple securities at a frequency up to a second. Bid and ask prices from the top of the orderbook are streamed. 


## Getting Started
All you need to do is to implement a method which is called everytime when new data comes in. 
The methods take 4 arguments which contains all the information you need for making trade decisions at the time. 
history is a dataframe containing the most recent history index by exchange, ticker and time 
portfolio is a dataframe containing the current exposure of your agent on all assets 
orders is a dataframe contating the open orders of your agent
trades is a dataframe containing the completed trades of your agent

Refer to the csv files attached to have a better idea on how the trades and history are stored in pedlar

Currrently we have implemeted two method to create and close orders 

### Installation
The client API is can be installed using:

```bash
pip3 install --no-cache-dir -U pedlar
```

### Usage

```python
from pedlar.agent import Agent

class MyAgent(Agent):
  """A trading agent."""
    def ondata(self, history=None, portfolio=None, orders=None, trades=None):
        # make trade decisions based on history, portfolio, orders and trades 
        self.create_order(exchange='TrueFX', ticker='GBP/USD', volume=1)
        if self.step == 3:
            self.close_order(orderid=1)

        return None 

```

### Repository Structure


### Prerequisites
All the extra packages required can be installed using:
```bash
pip3 install --no-cache-dir -U -r requirements.txt
```
 
## References
Attribution 

Data provided for free by IEX. View IEX’s Terms of Use. 
