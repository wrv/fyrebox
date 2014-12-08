import socket, ssl, json, threading

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

import auth
import fileops
import dirops
import logging


AUTHOPS = ['register', 'login']
FILEOPS = ['create', 'delete', 'read', 'write', 'rename', 'perm']
DIROPS = ['createdir', 'deletedir', 'readdir', 'writedir', 'renamedir', 'permdir']

class Chat(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "GETNAME"

    def connectionMade(self):
        self.sendLine("What's your name?")

    def connectionLost(self, reason):
        if self.name in self.users:
            del self.users[self.name]

    def lineReceived(self, line):
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)

    def handle_GETNAME(self, name):
        if name in self.users:
            self.sendLine("Name taken, please choose another.")
            return
        self.sendLine("Welcome, %s!" % (name,))
        self.name = name
        self.users[name] = self
        self.state = "CHAT"

    def handle_CHAT(self, message):
        message = "<%s> %s" % (self.name, message)
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)


class ChatFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Chat instances

    def buildProtocol(self, addr):
        return Chat(self.users)


reactor.listenTCP(10023, ChatFactory())
reactor.run()

"""
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
                pass


bindsocket = socket.socket()
bindsocket.bind(('localhost', 10023))
bindsocket.listen(5)

while True:
    newsocket, fromaddr = bindsocket.accept()
    connstream = ssl.wrap_socket(newsocket, server_side=True, certfile="certs/server.crt", keyfile="certs/server.key")
    try:
        t = threading.Thread(target=handleconnection, args=connstream)
        t.daemon = True
        t.start()
    finally:
        connstream.shutdown(socket.SHUT_RDWR)
        connstream.close()

"""