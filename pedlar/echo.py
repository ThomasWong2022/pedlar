"""Basic echo agent."""
from .agent import Agent


class EchoAgent(Agent):
  """Simple print incoming ticks."""
  def on_tick(self, bid, ask, time=None):
    """On tick handler."""
    print("Tick:", bid, ask, time)

  def on_bar(self, bopen, bhigh, blow, bclose, time=None):
    """On bar handler."""
    print("Bar:", bopen, bhigh, blow, bclose, time)

if __name__ == "__main__":
  import logging
  logging.basicConfig(level=logging.DEBUG)
  agent = EchoAgent.from_args()
  agent.run()
