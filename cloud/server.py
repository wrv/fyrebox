"""server.py file

This file contains the server descriptions
ref: https://docs.python.org/2/library/ssl.html#ssl-security
and Willy's server code
"""

import socket 
import ssl
import json
from settings import SERVER_NAME, SERVER_PORT, SERVER_BACKLOG, DEBUG


def do_something(connstream, data):
    print "do_something:", data

    data  = cleanup(data)
    if data is None: return False
    operation = data['operation'].lower()

    if operation == 'store':
        if ('username' not in data) or ('key' not in data):
            connstream.write("Store requires username and key fields\r\n")
            return False

        successful = store(data['username'], data['key'])
        if successful:
            connstream.write("OK")
        else:
            connstream.write("FAILED")

        return False

    elif operation == 'retrieve':
        if 'username' not in data:
            connstream.write("Store requires username field\r\n")
            return False

        key = retrieve(data['username'])
        if key is None:
            connstream.write("FAILED")
        else:
            connstream.write(key)
        return False

    elif operation == 'list':
        # only for debug
        if DEBUG:
            return False

    connstream.write("OPERATION NOT SUPPORTED")

    return False # finished with client

def cleanup(data):
    """Cleans received information and returns a cleaned-up dictionary"""
    data = data.strip()
    # make sure data is json
    try:
        data_dict = json.loads(data)
    except:
        print ":ERROR "
        return None

    if not isinstance(data_dict, dict):
        return None

    if 'operation' not in data_dict:
        return None

    return data_dict

def store(username, key):
    """If username is not in database, adds key and username to public key database"""
    #TODO
    return False

def list():
    """ For debugging purposes only.
    Lists all keys in db"""
    #TODO
    pass


def retrieve(username):
    """If username is in database, returns saved public key"""
    #TODO
    return None


def handle_connection(connstream):
    data = connstream.read()
    # null data means the client is finished with us
    while data:
        if not do_something(connstream, data):
            break
        data = connstream.read()


bindsocket = socket.socket()
bindsocket.bind((SERVER_NAME,  SERVER_PORT))
bindsocket.listen(SERVER_BACKLOG)


while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = ssl.wrap_socket(newsocket, 
                                server_side=True,
                                certfile="certs/server.crt",
                                keyfile="certs/server.key",
                                ssl_version=ssl.PROTOCOL_SSLv23)
    try:
        handle_connection(connstream)
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()


