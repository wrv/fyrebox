from Crypto.Cipher import AES
import base64
import os
import time
from OpenSSL import SSL
import socket
import json
from file import *
from crypto import *
from database import FileInfo, engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
openFiles = []
sslSocket = None
token = None
current_directory = None
username = None
def helpme(comSplit):
    print "stuff"

def create(file_name):
    file_key = os.urandom(32)
    #print file_key
    #print len(file_key)
    open(file_name, 'a').close()
    enc_file_name = encrypt(file_name, file_key)
    
    message = {}
    message['operation'] = "create"
    message['username'] = username
    message['token'] = token
    message['filename'] = enc_file_name
    message['dirname'] = current_directory
    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    #print response

    unique_id = response['fileid'] 
    encoded_file_key = file_key.encode('hex')
    new_file = FileInfo(file_name = unicode(file_name), unique_id = unique_id, file_key = encoded_file_key)
    session.add(new_file)
    session.commit()    
    
    return response

def write(file_name, content):
    file_key = session.query(FileInfo).filter_by(file_name = file_name)
    message = {}
    message['operation'] = "write"
    message['username'] = username
    message['token'] = token
    message['filename'] = encrypt(file_name, file_key.first().file_key.decode('hex'))
    message['fileid'] =  file_key.first().unique_id
    message['content'] = content

    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    #print response
    return response

def read(file_name):
    file_key = session.query(FileInfo).filter_by(file_name = file_name)
    message = {}
    message['operation'] = "read"
    message['username'] = username
    message['token'] = token
    message['filename'] = encrypt(file_name, file_key.first().file_key.decode('hex'))
    message['fileid'] =  file_key.first().unique_id
    #print message
    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    #print response
    return response

>>>>>>> ee94536643a865bd94af2bac44b3282e2118e4df
def main():
    serverConnection()
    register("asdfasdf", "test")
    create("testfile")
    write("testfile", "test")
    read("testfile")

def serverConnection():
    global sslSocket
    context = SSL.Context(SSL.SSLv23_METHOD)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 10023))
    sslSocket = socket.ssl(s)
    response = sslSocket.read()
    
def login(user, password):
    global token
    global current_directory
    global username
    username = user
    response = authHelper(username, password, "login")
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError

    token = response['token']
    current_directory = response['rootdir']
    os.chdir(current_directory)
    return

def register(user, password):
    global token
    global current_directory
    global username
    username = user
    response = authHelper(username, password, "register")
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError

    token = response['token']
    current_directory = response['rootdir']
    os.mkdir(current_directory)
    os.chdir(current_directory)
    return

def authHelper(username, password, command):
    message = {}
    message["username"] = username
    message["password"] = password
    message["operation"] = command
    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())
    return response

if __name__ == "__main__":
    main()
