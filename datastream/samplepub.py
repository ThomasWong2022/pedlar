import zmq
import time 



# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect('tcp://127.0.0.1:3000')

counter=0
while True and counter<10:
    counter+=1
    data='{"data":'+str(counter)+'}'
    socket.send_multipart([bytes('Sample','utf-8'), bytes(data,'utf-8')])
    time.sleep(1)
