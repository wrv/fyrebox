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
Session = sessionmaker(bind=engine)
session = Session()
openFiles = []
sslSocket = None
token = None
current_directory = None

def helpme(comSplit):
    print "stuff"
def create(file_name):
    file_key = os.urandom(32)
    open(file_name, 'a').close()
    file_name = encrypt(file_name, file_key)
    
    new_file = FileInfo(file_name = file_name, unique_id = unique_id, file_key = file_key)
    session.add(new_file)
    message = {}
    message['operation'] = "create"
    message['username'] = username
    message['token'] = token
    message['filename'] = file_name
    message['dirname'] = current_directory
    
    
def rm(comSplit):
    print "rm"
def write(comSplit):
    print "write"
def rename(comSplit):
    print "rename"
def perm(comSplit):
    print "perm"
def main():
    serverConnection()
def serverConnection():
    global sslSocket
    context = SSL.Context(SSL.SSLv23_METHOD)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 10023))
    sslSocket = socket.ssl(s)
    response = sslSocket.read()
    if message in response
        return
    
def login(username, password):
    global token
    global
    response = authHelper(sslSocket, username, password, "login")
    if 'message' in response:
        return
    token = response['token']
    current_directory = response['rootdir']
    os.chdir(current_directory)
    return
def register(username, password):
    global token
    global current_directory
    response = authHelper(username, password, "register")
    if 'message' in response:
        return
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
