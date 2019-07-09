const request = require('request');

const url = 'https://ws-api.iextrading.com/1.0/tops';
const socket = require('socket.io-client')(url);

var zmq = require('zeromq');
sock = zmq.socket('pub');

sock.connect('tcp://127.0.0.1:3000');
console.log('IEX Publisher connect to port 3000');

// list of tickers 

function onConnect(){
    socket.emit('subscribe', 'spy');
    console.log('Subscribe to SPY')
  };

socket.on('connect', onConnect);

socket.on('disconnect', () => console.log('Disconnected.'));

socket.on('message', message => {
    console.log(message);
    sock.send(['IEX', message]);
});