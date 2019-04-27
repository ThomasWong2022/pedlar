"""Basic echo agent."""
from agent import Agent


class EchoAgent(Agent):

  def __init__(self,**kwargs):
    self.counter = 0
    super().__init__(**kwargs)

  def onSample(self,tickerjson):
    print(tickerjson)
    self.counter +=1
    if self.counter%3 == 0:
      self.buy()
    if self.counter%3 == 2:
      self.close()

if __name__ == "__main__":
  import logging
  logging.basicConfig(level=logging.DEBUG)
  agent = EchoAgent.from_args()
  agent.run()
