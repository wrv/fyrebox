import socket, ssl, json

import auth
import fileops
import dirops
import logging


AUTHOPS = ['register', 'login']
FILEOPS = ['create', 'delete', 'read', 'write', 'rename', 'perm']
DIROPS = ['createdir', 'deletedir', 'readdir', 'writedir', 'renamedir', 'permdir']

def do_something(connstream, data):
    print "do_something:", data
    return False

def handleconnection(connstream):
    data = connstream.read()
    while data:
        data = connstream.read()
        pdata = json.load(data)
        if pdata['op'] in AUTHOPS:
            authop = pdata['op']
            if 'register' == authop:



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


