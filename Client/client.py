from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
import base64
import os
import time
from OpenSSL import SSL
import socket
import json
import ssl
import sys
import hashlib
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
password_hash = None
def print_error( msg):
    "Prints red message with a newline at the end"
    sys.stderr.write('\033[91m'+msg+'\033[0m \n')

def create(file_name):
    file_key = os.urandom(32)
    enc_file_name = encrypt(file_name, file_key)
    
    message = setupMessage("create")
    message['filename'] = enc_file_name
    message['dirname'] = current_directory
    
    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError

    unique_id = response['fileid'] 
    encoded_file_key = file_key.encode('hex')
    new_file = FileInfo(file_name = unicode(file_name), unique_id = unique_id, file_key = encoded_file_key)
    session.add(new_file)
    session.commit()    
    
    return response

def write(file_name, content):
    first = session.query(FileInfo).filter_by(file_name = file_name).first()
    file_key = first.file_key.decode('hex')
   
     message = setupMessage("write")
    message['filename'] = encrypt(file_name, file_key)
    message['fileid'] =  first.unique_id
    message['content'] = encrypt(content, file_key)

    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    
    return response

def read(file_name):
    file_key = session.query(FileInfo).filter_by(file_name = file_name)
    message = setupMessage("read")
    message['filename'] = encrypt(file_name, file_key.first().file_key.decode('hex'))
    message['fileid'] =  file_key.first().unique_id
    print message
    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    response['content'] = decrypt(response['content'],
file_key.first().file_key.decode('hex'))
    print response['content']
    return response

def rename(old_file_name, new_file_name):
    first = session.query(FileInfo).filter_by(file_name = old_file_name).first()
    file_key = first.file_key.decode('hex')
    unique_id = first.unique_id
    first.file_name = new_file_name
    message = setupMessage("rename")
    message['filename'] = encrypt(new_file_name, file_key)
    message['fileid'] = unique_id
    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    #os.rename(old_file_name, new_file_name)
    session.commit()
    return response

def delete(file_name):
    first = session.query(FileInfo).filter_by(file_name = file_name).first()
    file_key = first.file_key.decode('hex')
    unique_id = first.unique_id
    message = setupMessage("delete")
    message['filename'] = encrypt(file_name, file_key)
    message['fileid'] = unique_id
    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    session.delete(first)
    #os.unlink(file_name)
    session.commit()
    return response
def setupMessage(operation):
    message = {}
    message['operation'] = operation
    message['username'] = username
    message['token'] = token
    return message
def main():
    serverConnection()
    register("test4", "test")
    create("testfile")
    write("testfile", "test")
    read("testfile")
    rename("testfile", "testfile2")
    delete("testfile2")
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
    global password_hash
    username = user
    response = authHelper(username, password, "login")
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    password_hash = hashlib.sha256(password).hexdigest().decode('hex')
    print decrypt(encrypt("Blarg", password_hash), password_hash)
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
    password_hash = hashlib.sha256(password).digest()
    print password_hash
    print len(password_hash)
    print decrypt(encrypt("Blarg", password_hash), password_hash)

    token = response['token']
    current_directory = response['rootdir']
    os.mkdir(current_directory)
    os.chdir(current_directory)

    # create RSA Key
    rKey = RSA.generate(2048)
    f= open('mykey.pem', 'w')
    f.write(rKey.exportKey('PEM'))

    # send public Key to Cloud
    #try:
    pubKey = rKey.publickey().exportKey()

    cloud_connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cloud_ssl_sock = ssl.wrap_socket(cloud_connect_socket,
            ca_certs="../certs/server.crt",
            cert_reqs=ssl.CERT_REQUIRED)
    cloud_ssl_sock.connect(('localhost', 10029))
    cloud_ssl_sock.write(json.dumps(
        {'operation':'store','username': user,
            'key': pubKey}))
    #except Exception as e:
        #print e
        #print_error( "Saving Public Key to Cloud Server Failed")

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
