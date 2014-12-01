import socket, ssl, auth, logging


def do_something(connstream, data):
    print "do_something:", data
    return False

def handleconnection(connstream):
    data = connstream.read()
    while data:
        if not do_something(connstream, data):
            break
        data = connstream.read()


bindsocket = socket.socket()
bindsocket.bind(('localhost', 10023))
bindsocket.listen(5)

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = ssl.wrap_socket(newsocket, server_side=True, certfile="certs/server.crt", keyfile="certs/server.key")
    try:
        handleconnection(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()


