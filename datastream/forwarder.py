import zmq

def main():

    context = zmq.Context()
    # Socket facing clients
    frontend = context.socket(zmq.SUB)
    frontend.bind('tcp://127.0.0.1:3000')
    frontend.setsockopt(zmq.SUBSCRIBE, b"")  # All topics
    
    # Socket facing services
    backend = context.socket(zmq.PUB)
    backend.bind('tcp://127.0.0.1:7000')

    zmq.proxy(frontend, backend)
    

if __name__ == "__main__":
    main()