from Crypto.Cipher import AES
import base64
import os
import time
from OpenSSL import SSL
import socket
import json
from file import *
from crypto import *
def helpme(comSplit):
	print "stuff"
def create(comSplit):
	if len(comSplit) != 2:
		print "Improper command length, create <file name>"
		return
	file_key = os.urandom(32)
	file_name = comSplit[1]
	content = ""
	newFile = File(file_name, content, file_key, unique_id)
def rm(comSplit):
	print "rm"
def write(comSplit):
	print "write"
def rename(comSplit):
	print "rename"
def perm(comSplit):
	print "perm"
commands = {		"help"		: helpme,
			"create" 	: create,
			"rm" 		: rm,
			"write"		: write,
			"rename"	: rename,
			"perm"		: perm,
}
openFiles = []
sslSocket = None
token = None
current_directory = None
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
			key = os.urandom(32)
			print decrypt(encrypt("bladlsfjskdfj", key), key)
		else:
			print "Unrecognized command " + str(commandSplit[0])
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
    while 1:
        print "$ Type 1 to register, 2 to login"
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
        print response
        if 'message' in response:
                continue
        token = response['token']
        if cmd.strip() == "1":
                os.mkdir(username)
                os.chdir(username)
        if cmd.strip() == "2":
                os.chdir(username)
        return

if __name__ == "__main__":
	main()
