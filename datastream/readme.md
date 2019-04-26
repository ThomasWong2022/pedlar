Installation guide and requirements

Python and Pip 

sudo apt-get update

https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/

sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7
sudo apt install python3-pip

We will have both python 3.6(default) and python 3.7 running 

python3.7 -m pip install arctic
python3.7 -m pip install request_cache
python3.7 -m pip install pyzmq

Node js

sudo apt install nodejs npm

cd /folder with the stream 

npm install requests
npm install zeromq
npm install socket.io-client

https://linuxize.com/post/how-to-install-node-js-on-ubuntu-18.04/
https://docs.npmjs.com/cli/install


Run the scripts, these are the commands for WSL/Linux 

nodejs iex_tops.js
python3.7 truefx_hist
python3.7 forwarder.py 
python3.7 ondata.py > log/samplestream.txt 

For truxfx.py, need to set environmental variables for login names and password

export TRUEFX_USERNAME="XYZ" &&
export TRUEFX_PASSWORD="123" &&
python3.7 truefx.py

Acknowldgement 

Joe has written functions for TrueFX where I build upon to connect to Zeromq 


Design Documentation

For IEX only node.js server is supported so rather io.socket in python we need to set up node.js and npm

Currently, I am considering to add IEX as a pricing source to pedlar. It is a free source to use and provide real-time Level 1 and Level 2 data access to US Equities. The exchange accounts for around 2% of trades in the US. While the market share is small, the data generated is reasonable in a way for our students to learn. (Around 4GB of data per day uncompressed) 

Using the websocket API, I build a forwarder so that different pricing sources can be integrated and agents can subscribe to one single endpoint.  

https://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/devices/forwarder.html

IEX API documentation 

https://iextrading.com/developer/docs/#getting-started

TrueFX API documentation 
https://www.truefx.com/dev/data/TrueFX_MarketDataWebAPI_DeveloperGuide.pdf

