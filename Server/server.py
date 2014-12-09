import json

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, ssl
from twisted.python.modules import getModule

import auth
import fileops
import dirops
import log_client


AUTHOPS = ['register', 'login']
FILEOPS = ['create', 'delete', 'read', 'write', 'rename', 'perm']
DIROPS = ['createdir', 'deletedir', 'readdir', 'writedir', 'renamedir', 'permdir']

class FileServer(LineReceiver):

    def __init__(self, users):
        self.state = "UNAUTHENTICATED"

    def connectionMade(self):
        self.sendLine("Connected")

    def connectionLost(self, reason):
        pass

    def lineReceived(self, line):
        if self.state == "UNAUTHENTICATED":
            self.handle_UNAUTHENTICATED(line)
        else:
            self.handle_AUTHENTICATED(line)

    #Will authenticate the user based on given info
    def handle_UNAUTHENTICATED(self, message):
        try:
            parsedjson = json.loads(message)
        except:
            print "error in json. msg: " + message
            return

        token = None
        op = parsedjson['operation']
        if op not in AUTHOPS:
            self.sendLine('{"message":"failure"}')
            return

        if "register" == op:
            print "registering"
            token = auth.register(parsedjson['username'], parsedjson['password'])

        if "login" == op:
            print "logging in"
            token = auth.login(parsedjson['username'], parsedjson['password'])
        
        if token:
            print "token successful"
            response = {}
            response['username'] = parsedjson['username']
            response['token'] = token
            self.sendLine(json.dumps(response))
            self.state = "AUTHENTICATED"
        else:
            print "token unsuccessful"
            self.sendLine('{"message":"failure"}')
            return

    def handle_AUTHENTICATED(self, message):
        try:
            parsedjson = json.loads(message)
        except:
            print "error in json. msg: " + message
            return

        op = parsedjson['operation']
        if op not in FILEOPS or op not in DIROPS:
            self.sendLine('{"message":"failure"}')
            return

        username = parsedjson['username']
        token = parsedjson['token']
        #for organizational structure
        if op in FILEOPS:
            filename = parsedjson['filename']

            if "create" == op:
                if fileops.create(filename, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "delete" == op:
                if fileops.delete(filename, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "read" == op:
                if fileops.read(filename, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "write" == op:
                content = parsedjson['content']
                if fileops.write(filename, content, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "rename" == op:
                newname = parsedjson['newname']
                if fileops.rename(filename, newname, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "perm" == op:
                perms = parsedjson['permissions']
                if fileops.perm(filename, perms, username, token):
                    self.sendLine('{"message":"success"}')
                    return

        if op in DIROPS:
            dirname = parsedjson['dirname']

            if "createdir" == op:
                if dirops.createdir(dirname, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "deletedir" == op:
                if dirops.deletedir(dirname, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "readdir" == op:
                if dirops.readdir(dirname, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "renamedir" == op:
                newname = parsedjson['newname']
                if dirops.renamedir(dirname, newname, username, token):
                    self.sendLine('{"message":"success"}')
                    return
            elif "permdir" == op:
                perms = parsedjson['permissions']
                if dirops.permdir(dirname, perms, username, token):
                    self.sendLine('{"message":"success"}')
                    return


        self.sendLine('{"message":"failure"}')
        return


class FileServerFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Chat instances

    def buildProtocol(self, addr):
        return FileServer(self.users)

certData = getModule(__name__).filePath.sibling('server.pem').getContent()
certificate = ssl.PrivateCertificate.loadPEM(certData)
reactor.listenSSL(10023, FileServerFactory(), certificate.options())
reactor.run()

# def do_something(connstream, data):
#     print "do_something:", data
#     return False

# def handleconnection(connstream):
#     data = connstream.read()
#     while data:
#         data = connstream.read()
#         pdata = json.load(data)
#         if pdata['op'] in AUTHOPS:
#             authop = pdata['op']
#             if 'register' == authop:
#                 pass


# bindsocket = socket.socket()
# bindsocket.bind(('localhost', 10023))
# bindsocket.listen(5)

# while True:
#     newsocket, fromaddr = bindsocket.accept()
#     connstream = ssl.wrap_socket(newsocket, server_side=True, certfile="certs/server.crt", keyfile="certs/server.key")
#     try:
#         t = threading.Thread(target=handleconnection, args=connstream)
#         t.daemon = True
#         t.start()
#     finally:
#         connstream.shutdown(socket.SHUT_RDWR)
#         connstream.close()
