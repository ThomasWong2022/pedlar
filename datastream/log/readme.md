Market Data publisher/subscriber model with zeromq

A publisher, forwarder and subscriber model is used so that multiple servers can publish market data and multiple clients can subscribe data they want 

It can be used with pedlar in a local environment and by hosted on AWS with suitable modifications to the port settings 

Organization 

forwarder.py defines the port where the publisher and subscriber should bind 

Data Sources supported 

US Equities: IEX (tick,websocket) 
Forex: TrueFX (tick,HTTP) 

Delayed price data 
Stooq 
Yahoo 

