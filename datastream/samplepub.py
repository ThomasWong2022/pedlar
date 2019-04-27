import zmq
import time 
import json


# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect('tcp://127.0.0.1:3000')

counter =0
while True:
    counter += 1
    data = dict()
    data['bid'] = counter
    data['ask'] = counter+0.5
    data['symbol'] = 'ICL'
    print(data)
    socket.send_multipart([bytes('Sample', 'utf-8'), bytes(json.dumps(data), 'utf-8')])
    time.sleep(1)
