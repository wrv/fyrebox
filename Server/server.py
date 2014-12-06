import socket
import ssl
import json
import auth
import logging

#code used from here: http://carlo-hamalainen.net/blog/2013/1/24/python-ssl-socket-echo-test-with-self-signed-certificate

AUTHOPS = ['register', 'login']
FILEOPS = ['create', 'delete', 'read', 'write', 'rename']
def do_something(connstream, data):
    print "do_something:", data
    return False

def handleconnection(connstream):
    data = connstream.read()
    while data:
        data = connstream.read()
        pdata = json.load(data)
        if pdata


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


