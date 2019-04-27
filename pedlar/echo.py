"""Basic echo agent."""
from agent import Agent


class EchoAgent(Agent):

  def onSample(self,tickerjson):
    print(tickerjson)

if __name__ == "__main__":
  import logging
  logging.basicConfig(level=logging.DEBUG)
  agent = EchoAgent.from_args()
  agent.run()
