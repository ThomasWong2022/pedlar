

# :chart_with_upwards_trend: pedlar
Pedlar is an algorithmic trading platform for Python designed for trading events, competitions and sessions such as Algothons. It uses real time data from IEX and TrueFX 


## Getting Started


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
    def ondata(self, verbose=False):
        # make trade decisions 
        # self.history gives the most recent price history 
        # self.portfolio give current holdings 
        # self
        self.create_order(exchange='TrueFX', ticker='GBP/USD', volume=1)
        if self.step == 3:
            self.close_order(orderid=1)

        return None 

if __name__ == "__main__":
  import logging
  logging.basicConfig(level=logging.DEBUG)
  agent = MyAgent.from_args()
  agent.run()
```

The extra parameters are parsed from the command line and can be run using:

```bash
python3 -u myagent.py -h
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
