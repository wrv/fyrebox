from Crypto.Cipher import AES
import base64
import os
import time
from OpenSSL import SSL
import socket
import json

def help(comSplit):
	print "stuff"
def create(comSplit):
	if len(comSplit) != 2:
		print "Improper command length, create <file name>"
		return
	key = os.urandom(32)
	fileName = comSplit[1]
	content = ""
	identifier = username + str(time.time()) + str(base64.b64encode(os.urandom(32)))
	newFile = File(fileName, content, key, identifier)
	openFiles.append(newFile)
	print "fileName = " + fileName + " content = " + content + " key = " + str(key) + " identifier = " + str(identifier)
def rm(comSplit):
	print "rm"
def write(comSplit):
	print "write"
def rename(comSplit):
	print "rename"
def perm(comSplit):
	print "perm"
commands = {"help"		: help,
			"create" 	: create,
			"rm" 		: rm,
			"write"		: write,
			"rename"	: rename,
			"perm"		: perm,
}
openFiles = []
sslSocket = None
token = None
class File:
	#"""A simple class that represents an in memory file, useful for manipulation on the client side"""
	def __init__(self, fileName, content, key, identifier):
		self.fileName = fileName
		self.content = content
		self.key = key
		self.identifier = identifier
	def write(self, content, token):
		response = sendWrite(self.fileName, content, token)
		if response != -1:
			self.content = content
			return 0
		return -1
class WriteError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def main():
    serverConnection()
    login()
    while(1):
		command = raw_input("$ ")
		commandSplit = command.split()
		if len(commandSplit) == 0:
			continue
		if commandSplit[0] in commands:
			com = commandSplit[0]
			commands[com](commandSplit)
			decrypt(encrypt("bladlsfjskdfj"), key)
		else:
			print "Unrecognized command " + str(commandSplit[0])
def encrypt(content):
	global key
	BLOCK_SIZE = 32
	PADDING = '{'
	pad = lambda s: s + (BLOCK_SIZE - (len(s) % BLOCK_SIZE)) * PADDING
	EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
	key = os.urandom(BLOCK_SIZE)
	print "encryption key:",key
	cipher = AES.new(key)
	encoded = EncodeAES(cipher,content);
	print "Encrypted string:", encoded
	return encoded
def decrypt(content, key):
	PADDING = "{"
	DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
	encryption = content
	cipher = AES.new(key)
	decoded = DecodeAES(cipher, encryption)
	print decoded
def serverConnection():
    global sslSocket
    context = SSL.Context(SSL.SSLv23_METHOD)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 10023))
    sslSocket = socket.ssl(s)
    response = sslSocket.read()
    print response
def login():
    global sslSocket
    global token
    print "$ Type 1 to register, 2 to login"
    while 1:
        cmd = raw_input("$ ")
        message = {}
        if cmd.strip() == "1":
            message["operation"] = "register"
        elif cmd.strip() == "2":
            message["operation"] = "login"
        else:
            print "Improper command"
            continue 
        username = raw_input("$ username = ")
        password = raw_input("$ password = ")
        message["username"] = username
        message["password"] = password
        encoded = json.dumps(message)
        print encoded
        sslSocket.write(encoded)
        response = sslSocket.read()
        response = json.loads(response)
        token = response['token']
        print response
        print token

if __name__ == "__main__":
	main()
