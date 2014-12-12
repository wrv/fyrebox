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
cloud_ssl_sock = None
token = None
current_directory = None
username = None
password_hash = None
private_key = None
def print_error( msg):
    "Prints red message with a newline at the end"
    sys.stderr.write('\033[91m'+msg+'\033[0m \n')
def retrieve_public_key(username):
    message = {}
    message['operation'] = "retrieve"
    message['username'] = username
    cloud_ssl_sock.write(json.dumps(message))
    response = cloud_ssl_sock.read()
    response = json.loads(response)
    pub_key = RSA.importKey(response['key'])
    return pub_key
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
    encoded_file_key = encrypt(file_key.encode('hex'), password_hash)
    content_hash = hashlib.sha256("").digest().encode('hex')
    new_file = FileInfo(file_name = file_name, unique_id = unique_id, file_key =
encoded_file_key, content_hash = content_hash)
    session.add(new_file)
    session.commit()    
    
    return response
def create_dir(dir_name):
    dir_key = os.urandom(32)
    enc_dir_name = encrypt(dir_name, dir_key)

    message = setupMessage("createdir")
    message['dirname'] = enc_dir_name
    message['parentdir'] = current_directory

    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError

    unique_id = response['dirid']
    encoded_dir_key = encrypt(dir_key.encode('hex'), password_hash)
    content_hash = hashlib.sha256("").digest().encode('hex')
    new_dir = FileInfo(file_name = dir_name, unique_id = unique_id, file_key =
encoded_dir_key, content_hash = content_hash)
    session.add(new_dir)
    session.commit()
    return enc_dir_name
def write(file_name, content):
    first = session.query(FileInfo).filter_by(file_name = file_name).first()
    
    file_key = get_file_key(file_name)
    unique_id = get_unique_id(file_name) 

    message = setupMessage("write")
    message['filename'] = encrypt(file_name, file_key)
    message['fileid'] =  unique_id
    message['content'] = encrypt(content, file_key)

    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    first.content_hash = hashlib.sha256(content).digest().encode('hex')
    session.commit()
    return response

def read(file_name):
    first = session.query(FileInfo).filter_by(file_name = file_name).first()
    file_key = get_file_key(file_name)
    unique_id = get_unique_id(file_name)
    
    message = setupMessage("read")
    message['filename'] = encrypt(file_name, file_key)
    message['fileid'] =  unique_id

    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError

    response['content'] = decrypt(response['content'], file_key)
    content_hash = hashlib.sha256(response['content']).digest().encode('hex')
    if content_hash != first.content_hash:
        print "SOMEONE HAS TAMPERED WITH THIS FILE"
        raise ValueError
    return response
def read_dir(dir_name):
    first = session.query(FileInfo).filter_by(file_name = dir_name).first()
    dir_key = get_file_key(dir_name)
    unique_id = get_unique_id(dir_name)

    message = setupMessage("readdir")
    message['dirname'] = encrypt(dir_name, dir_key)
    message['dirid'] = unique_id

    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    return response
def rename(old_file_name, new_file_name):
    first = session.query(FileInfo).filter_by(file_name = old_file_name).first()

    file_key = get_file_key(old_file_name)
    unique_id = get_unique_id(old_file_name)
    first.file_name = new_file_name

    message = setupMessage("rename")
    message['filename'] = encrypt(new_file_name, file_key)
    message['fileid'] = unique_id

    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError

    session.commit()
    
    return response

def delete(file_name):
    first = session.query(FileInfo).filter_by(file_name = file_name).first()
    file_key = get_file_key(file_name)
    unique_id = get_unique_id(file_name)

    message = setupMessage("delete")
    message['filename'] = encrypt(file_name, file_key)
    message['fileid'] = unique_id

    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())

    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError

    session.delete(first)
    session.commit()
    
    return response
def perm(file_name, new_user, permission):
    file_key = get_file_key(file_name)
    unique_id = get_unique_id(file_name)
    public_key = retrieve_public_key(new_user)
    encrypted_key = public_key.encrypt(file_key,32)[0].encode('hex')
    message = setupMessage("perm")
    message['filename'] = encrypt(file_name, file_key)
    message['fileid'] = unique_id
    message['permissions'] = (permission, new_user, encrypted_key)
    print message
    sslSocket.write(json.dumps(message))
    response = json.loads(sslSocket.read())
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    return
 
def setupMessage(operation):
    message = {}
    message['operation'] = operation
    message['username'] = username
    message['token'] = token
    return message
def get_file_key(file_name):
    first = session.query(FileInfo).filter_by(file_name = file_name).first()
    file_key = decrypt(first.file_key, password_hash).decode('hex')
    return file_key
def get_unique_id(file_name):
    first = first = session.query(FileInfo).filter_by(file_name = file_name).first()
    unique_id = first.unique_id
    return unique_id
def main():
    global current_directory
    serverConnection()
    register("test", "test")
    dirid = create_dir("testdir")
    current_directory = dirid
    create("testfile")
    print read_dir("testdir")
    #create("testfile4")
    #write("testfile", "test")
    #read("testfile")
    #rename("testfile", "testfile2")
    #delete("testfile2")
    #login("test", "test")
    #perm("test", "test2", True)
def serverConnection():
    global sslSocket
    global cloud_ssl_sock
    context = SSL.Context(SSL.SSLv23_METHOD)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 10023))
    sslSocket = socket.ssl(s)
    response = sslSocket.read()
    cloud_connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cloud_ssl_sock = ssl.wrap_socket(cloud_connect_socket,
            ca_certs="certs/server.crt",
            cert_reqs=ssl.CERT_REQUIRED)
    cloud_ssl_sock.connect(('localhost', 10029))
    cloud_ssl_sock.read()
    
def login(user, password):
    global token
    global current_directory
    global username
    global password_hash
    global private_key
    username = user
    response = authHelper(username, password, "login")
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    password_hash = hashlib.sha256(password).digest()
    token = response['token']
    current_directory = response['rootdir']
    os.chdir(current_directory)
    private_key = RSA.importKey(open('mykey.pem', 'r').read())
    return

def register(user, password):
    global token
    global current_directory
    global username
    global password_hash
    username = user
    response = authHelper(username, password, "register")
    if 'message' in response:
        if response['message'] == 'failure':
            raise ValueError
    password_hash = hashlib.sha256(password).digest()

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
