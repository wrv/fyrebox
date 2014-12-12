#from file import *
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from OpenSSL import SSL
from crypto import *
from database import FileInfo, engine
from sqlalchemy.orm import sessionmaker
import base64
import hashlib
import json
import os
import socket
import ssl
import sys
import time
from settings import (CLOUD_SERVER_NAME, CLOUD_SERVER_PORT,
                        FILE_SERVER_NAME, FILE_SERVER_PORT )
from settings import CLIENT_DEBUG as DEBUG

Session = sessionmaker(bind=engine)
session = Session()

class Client(object):
    """
    Nomenclature:
            fs --> file server
            cs --> cloud (key) server
    """
    def __init__(self, cs_host=CLOUD_SERVER_NAME,
            cs_port=CLOUD_SERVER_PORT,
            fs_host=FILE_SERVER_NAME,
            fs_port=FILE_SERVER_PORT):

        # servers
        self.cs_host = cs_host
        self.cs_port = cs_port
        self.fs_host = fs_host
        self.fs_port = fs_port

        # sockets
        self.fs_sslSocket = None
        self.cs_sslSocket = None

        # user_cred
        self.username = None
        self.token = None
        self.password_hash = None
        self.private_key = None

        #other
        self.current_directory = None
        self.root_directory = None
        # connect to servers
        self.serverConnection()


    ########################################
    # Util Functions
    ########################################
    @staticmethod
    def send_and_get(with_socket,  message):
        """ Will json dump and decode"""
        with_socket.write(json.dumps(message))
        response = with_socket.read()
        try:
            response = json.loads(response)
        except Exception as e:
            if DEBUG:
                print "response : ", response
                print e
            raise 

        if 'message' in response:
            if response['message'] == 'failure':
                if DEBUG:
                    print response
                raise ValueError

        return response

    def retrieve_public_key(self, username):
        message = {}
        message['operation'] = "retrieve"
        message['username'] = username
        # TODO try, exempt
        response = self.send_and_get(self.cs_sslSocket,  message)
        pub_key = RSA.importKey(response['key'])
        return pub_key

    def setupMessage(self, operation):
        return {'operation' : operation,
                'username' : self.username,
                'token' : self.token}

    def get_file_key(self, file_name):
        first = session.query(FileInfo).filter_by(file_name=file_name).first()
        file_key = decrypt(first.file_key, self.password_hash).decode('hex')
        return file_key


    def get_unique_id(self, file_name):
        first = first = session.query(FileInfo).filter_by(
            file_name=file_name).first()
        unique_id = first.unique_id
        return unique_id

    def serverConnection(self):

        ## connect to file server over SSL
        ## must have certificate present
        fs_connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.fs_sslSocket = ssl.wrap_socket(fs_connect_socket,
                                         ca_certs="certs/file_server.crt",
                                         cert_reqs=ssl.CERT_REQUIRED)
        self.fs_sslSocket.connect((FILE_SERVER_NAME, FILE_SERVER_PORT))
        self.fs_sslSocket.read() # connect success


        ## connect to cloud server over SSL
        ## must have certificate present
        cloud_connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cs_sslSocket = ssl.wrap_socket(cloud_connect_socket,
                                         ca_certs="certs/cloud_server.crt",
                                         cert_reqs=ssl.CERT_REQUIRED)
        self.cs_sslSocket.connect((CLOUD_SERVER_NAME, CLOUD_SERVER_PORT))
        self.cs_sslSocket.read() # connect success

    ########################################
    # Actions Functions
    ########################################
    def create_dir(self, dir_name):
        dir_key = os.urandom(32)
        enc_dir_name = encrypt(dir_name, dir_key)
                    
        message = self.setupMessage("createdir")
        message['dirname'] = enc_dir_name
        message['parentdir'] = self.current_directory

        response = self.send_and_get(self.fs_sslSocket, message)
        if DEBUG: print response

        unique_id = response['data']['dir_id']
        encoded_dir_key = encrypt(dir_key.encode('hex'), self.password_hash)
        content_hash = hashlib.sha256("").digest().encode('hex')
        new_dir = FileInfo(file_name = dir_name, unique_id = unique_id, file_key =
    encoded_dir_key, content_hash = content_hash)
        session.add(new_dir)
        session.commit()
        #return enc_dir_name
        return response

    def read_dir(self,dir_name):
        if dir_name == self.root_directory:
            message = self.setupMessage("readdir")
            message['dirname'] = dir_name
            message['dirid'] = dir_name
        else:
            first = session.query(FileInfo).filter_by(file_name = dir_name).first()
            dir_key = self.get_file_key(dir_name)
            unique_id = self.get_unique_id(dir_name)

            message = self.setupMessage("readdir")
            message['dirname'] = encrypt(dir_name, dir_key)
            message['dirid'] = unique_id
                    
        response = self.send_and_get(self.fs_sslSocket, message)
        content = response['content']
        file_list = []
        print content
        for element in content:
            first = session.query(FileInfo).filter_by(unique_id = element).first()
            file_list.append(first.file_name)
        file_list.sort()
            
        return file_list

    def create(self, file_name):
        file_key = os.urandom(32)
        enc_file_name = encrypt(file_name, file_key)

        message = self.setupMessage("create")
        message.update({'filename': enc_file_name,
                        'dirname': self.current_directory})

        response = self.send_and_get(self.fs_sslSocket, message)

        unique_id = response['fileid']
        encoded_file_key = encrypt(file_key.encode('hex'), self.password_hash)
        content_hash = hashlib.sha256("").digest().encode('hex')

        new_file = FileInfo(file_name=file_name,
                            unique_id=unique_id,
                            file_key=encoded_file_key,
                            content_hash=content_hash)
        # TODO db session attribute
        session.add(new_file)
        session.commit()

        return response


    def write(self, file_name, content):
        first = session.query(FileInfo).filter_by(file_name=file_name).first()

        file_key = self.get_file_key(file_name)
        unique_id = self.get_unique_id(file_name)

        message = self.setupMessage("write")
        message['filename'] = encrypt(file_name, file_key)
        message['fileid'] = unique_id
        message['content'] = encrypt(content, file_key)

        response = self.send_and_get(self.fs_sslSocket, message)

        first.content_hash = hashlib.sha256(content).digest().encode('hex')
        session.commit()

        return response


    def read(self, file_name):
        first = session.query(FileInfo).filter_by(file_name=file_name).first()
        file_key = self.get_file_key(file_name)
        unique_id = self.get_unique_id(file_name)

        message = self.setupMessage("read")
        message['filename'] = encrypt(file_name, file_key)
        message['fileid'] = unique_id

        response = self.send_and_get(self.fs_sslSocket, message)

        response['content'] = decrypt(response['content'], file_key)
        content_hash = hashlib.sha256(response['content']).digest().encode('hex')

        if content_hash != first.content_hash:
            print "SOMEONE HAS TAMPERED WITH THIS FILE"
            if DEBUG:
                print response
            raise ValueError
        return response

    def rename(self, old_file_name, new_file_name):
        first = session.query(FileInfo).filter_by(
            file_name=old_file_name).first()

        file_key = self.get_file_key(old_file_name)
        unique_id = self.get_unique_id(old_file_name)
        first.file_name = new_file_name

        message = self.setupMessage("rename")
        message['filename'] = encrypt(new_file_name, file_key)
        message['fileid'] = unique_id

        response = self.send_and_get(self.fs_sslSocket, message)

        session.commit()

        return response


    def delete(self, file_name):
        first = session.query(FileInfo).filter_by(file_name=file_name).first()
        file_key = self.get_file_key(file_name)
        unique_id = self.get_unique_id(file_name)

        message = self.setupMessage("delete")
        message['filename'] = encrypt(file_name, file_key)
        message['fileid'] = unique_id

        response = self.send_and_get(self.fs_sslSocket, message)

        session.delete(first)
        session.commit()

        return response


    def perm(self, file_name, new_user, permission):
        file_key = self.get_file_key(file_name)
        unique_id = self.get_unique_id(file_name)
        public_key = self.retrieve_public_key(new_user)
        encrypted_key = public_key.encrypt(file_key, 32)[0].encode('hex')
        message = self.setupMessage("perm")
        message['filename'] = encrypt(file_name, file_key)
        message['fileid'] = unique_id
        message['permissions'] = (permission, new_user, encrypted_key)

        print message ## TODO remove

        response = self.send_and_get(self.fs_sslSocket, message)
        return response


    def login(self, user, password):
        username = user

        response = self.authHelper(username, password, "login")

        # set class attributes
        self.username = username
        self.password_hash = hashlib.sha256(password).digest()
        self.token = response['token']
        self.current_directory = response['rootdir']
        self.root_directory = response['rootdir']
        os.chdir(self.current_directory) # TODO new separate dir for files?
        try:
            self.private_key = RSA.importKey(open('mykey.pem', 'r').read())
        except Exception as e:
            print "ERROR: could not get private key"


    def register(self, username, password):
        response = self.authHelper(username, password, "register")

        # set class attributes
        self.username = username
        self.password_hash = hashlib.sha256(password).digest()
        self.token = response['token']
        self.current_directory = response['rootdir']
        self.root_directory = response['rootdir']
        # create user folder
        os.mkdir(self.current_directory)
        os.chdir(self.current_directory)

        # create RSA Key
        rKey = RSA.generate(2048)
        f = open('mykey.pem', 'w')
        f.write(rKey.exportKey('PEM'))

        pubKey = rKey.publickey().exportKey()

        message = {'operation': 'store',
                'username': self.username,
                'key': pubKey}

        response = self.send_and_get(self.cs_sslSocket, message)
        return response


    def authHelper(self, username, password, command):
        message = {
                "username":username,
                "password":password,
                "operation":command}

        self.fs_sslSocket.write(json.dumps(message))
        response = json.loads(self.fs_sslSocket.read())
        if 'message' in response:
            if response['message'] == 'failure':
                if DEBUG:
                    print response
                raise ValueError
        return response


def main():
    c = Client()
    c.register("test", "test")
    c.create("testfile")
    c.create("testfile2")
    c.create("testfile3")
    print c.read_dir(c.current_directory) 

def print_error(msg):
    "Prints red message with a newline at the end"
    sys.stderr.write('\033[91m' + msg + '\033[0m \n')

if __name__ == "__main__":
    main()
