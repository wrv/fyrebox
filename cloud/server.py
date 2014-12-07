"""server.py file

This file contains the server descriptions
ref: https://docs.python.org/2/library/ssl.html#ssl-security
and Willy's server code
"""

import socket 
import ssl


def do_something(connstream, data):
    print "do_something:", data
    return False # finished with client

def handle_connection(connstream):
    data = connstream.read()
    # null data means the client is finished with us
    while data:
        if not do_something(connstream, data):
            break
        data = connstream.read()


bindsocket = socket.socket()
bindsocket.bind(('localhost', 10023))
bindsocket.listen(5)


# setup context if working in 2.7.9 onwards - TODO: decide

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = ssl.wrap_socket(newsocket, server_side=True,
            certfile="certs/server.crt", keyfile="certs/server.key")
    try:
        handle_connection(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()


