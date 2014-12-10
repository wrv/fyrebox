"""server.py file

This file contains the server descriptions
ref: https://docs.python.org/2/library/ssl.html#ssl-security
"""

import socket 
import asyncore

import ssl
import json
from settings import SERVER_NAME, SERVER_PORT, SERVER_BACKLOG, DEBUG
from database import PublicKey, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine) # session class
session = Session() # TODO change to class, one session per connection


#class RequestHandler(asyncore.dispatcher_with_send):
    #def handle_read(self):
        #data = self.recv(8192)
        #if data:
            #self.send(data)


        #newsocket, fromaddr = bindsocket.accept()
        #connstream = ssl.wrap_socket(newsocket, 
                                #server_side=True,
                                #certfile="certs/server.crt",
                                #keyfile="certs/server.key",
                                #ssl_version=ssl.PROTOCOL_SSLv23)
    #try:
        #handle_connection(connstream)
    #finally:
        #connstream.shutdown(socket.SHUT_RDWR)
        #connstream.close()

#class FyreBoxCloudServer(asyncore.dispatcher):
    #def __init__(self, host, port):
        #asyncore.dispatcher.__init__(self)
        #self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.set_reuse_addr()
        #self.bind((host, port))
        #self.listen(SERVER_BACKLOG)
    #def handle_accept(self):
        #pair = self.accept()
        #if pair is not None:
            #sock, addr = pair
            #print 'Incoming connection from %s' % repr(addr)
            #handler = RequestHandler(sock)

def process_data(connstream, data):
    print "process_data:", data

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
            connstream.write("Retrieve requires username field\r\n")
            return False

        key = retrieve(data['username'])
        if key is None:
            connstream.write("User not found")
        else:
            connstream.write(key)
        return False

    elif operation == 'list':
        # only for debug
        if DEBUG:
            connstream.write(str(list()))
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

def store(username_, key_):
    """If username is not in database, adds key and username to public key database"""
    try:
        pub_key = PublicKey(username=username_, key=key_)
        session.add(pub_key)
        return True
    except:
        return False

def list():
    """ For debugging purposes only.
    Lists all keys in db"""
    return session.query(PublicKey).all()

def retrieve(username_):
    """If username is in database, returns saved public key. None otherwise"""
    try:
        user = session.query(PublicKey).filter_by(username=username_).first()
        return user
    except:
        return None


def handle_connection(connstream):
    data = connstream.read()
    # null data means the client is finished with us
    while data:
        if not process_data(connstream, data):
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


