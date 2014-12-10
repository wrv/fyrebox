import json

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, ssl
from twisted.python.modules import getModule

from auth import login, register
import fileops
import dirops
import time
import log_client

##
# To Do:
#  - change the prints to logs
#  - rpc the auth

#Organization of all our operations for authentication, files, and directory
AUTHOPS = ['register', 'login']
FILEOPS = ['create', 'delete', 'read', 'write', 'rename', 'perm']
DIROPS = ['createdir', 'deletedir', 'readdir', 'writedir', 'renamedir', 'permdir']

#Fail and success messages to respond to the client with
MSGFAIL = '{"message":"failure"}'
MSGSUCCESS = '{"message":"success"}'

##
# FileServer(lineReceiver)
#
# Class that handles each connection
class FileServer(LineReceiver):

    def __init__(self, users):
        self.state = "UNAUTHENTICATED"

    ##
    # connectionMade()
    #
    # Run whenever the initial condition is made with the server
    def connectionMade(self):
        #log_client.log("Connection made")
        self.sendLine('{"message":"connected"}')

    ##
    # connectionLost(reason)
    #
    # Run whenever the connection is lost with a client
    def connectionLost(self, reason):
        pass

    ##
    # dataReceived(data)
    #
    # Runs after connection is made and data is sent to the server
    def dataReceived(self, data):
        #print data
        if self.state == "UNAUTHENTICATED":
            self.handle_UNAUTHENTICATED(data)
        else:
            self.handle_AUTHENTICATED(data)

    ##
    # lineReceived(line)
    #
    # Runs after connection is made and data is sent to the server
    def lineReceived(self, line):
        #print line
        if self.state == "UNAUTHENTICATED":
            self.handle_UNAUTHENTICATED(line)
        else:
            self.handle_AUTHENTICATED(line)

    ##
    # fail()
    #
    # User made function to call so the client can receive an error message
    def fail(self):
        self.sendLine(MSGFAIL)

    ##
    # handle_UNAUTHENTICATED()
    #
    # If the state is UNAUTHENTICATED then this function will try to authenticate
    # the user by either making a new user or logging in
    def handle_UNAUTHENTICATED(self, message):
        try:
            parsedjson = json.loads(message)
            op = parsedjson['operation']
        except:
            print "error in json. msg: " + message
            return

        token = None
        rootdir = None

        if op not in AUTHOPS:
            self.fail()
            return

        if "register" == op:
            print "registering"
            (token, rootdir) = register(parsedjson['username'], parsedjson['password'])

        if "login" == op:
            print "logging in"
            (token, rootdir) = login(parsedjson['username'], parsedjson['password'])

        
        if token:
            if rootdir:
                print "token successful"
                response = {}
                response['username'] = parsedjson['username']
                response['token'] = token
                response['timestamp'] = time.time()
                response['rootdir'] = rootdir
                self.sendLine(json.dumps(response))
                self.state = "AUTHENTICATED"
        else:
            print "token unsuccessful"
            self.fail()
            return

    ##
    # handle_AUTHENTICATED()
    #
    # If the state is AUTHENTICATED then this function will do various operations
    # on the server for files and databases
    def handle_AUTHENTICATED(self, message):
        try:
            parsedjson = json.loads(message)
            op = parsedjson['operation']
        except:
            print "error in json 1. msg: " + message
            return

        if op not in FILEOPS and op not in DIROPS:
            print "error in json 2. msg: " + message
            self.fail()
            return

        try:
            username = parsedjson['username']
            token = parsedjson['token']
        except:
            print "error in json 3. msg: " + message
            return

        #### File Operations
        if op in FILEOPS:
            try:
                filename = parsedjson['filename']
            except:
                print "error in json 4. msg: " + message
                self.fail()
                return

            if "create" == op:
                try:
                    dirname = parsedjson['dirname']
                except:
                    self.fail()
                    return

                output = fileops.create(filename, dirname, username, token)
                if output:
                    response = {}
                    response['message'] = 'success'
                    response['fileid'] = output
                    self.sendLine(json.dumps(response))
                    return
                self.fail()
                return

            #All following operations will rely on the fileid
            fileid = parsedjson['fileid']
            if "delete" == op:
                if fileops.delete(fileid, filename, username, token):
                    self.sendLine(MSGSUCCESS)
                    return

            elif "read" == op:
                output = fileops.read(fileid, filename, username, token)
                if output:
                    response = {}
                    response['message'] = 'success'
                    response['content'] = output
                    self.sendLine(json.dumps(response))
                    return

            elif "write" == op:
                content = parsedjson['content']
                if fileops.write(fileid, filename, content, username, token):
                    self.sendLine(MSGSUCCESS)
                    return
            elif "rename" == op:
                if fileops.rename(fileid, filename, username, token):
                    self.sendLine(MSGSUCCESS)
                    return
            elif "perm" == op:
                perms = parsedjson['permissions']
                if fileops.perm(fileid, filename, perms, username, token):
                    self.sendLine(MSGSUCCESS)
                    return

        #### Directory Operations
        if op in DIROPS:
            dirname = parsedjson['dirname']

            if "createdir" == op:
                output = dirops.createdir(dirname, username, token)
                if output:
                    response = {}
                    response['message'] = 'success'
                    response['dirid'] = output
                    self.sendLine(json.dumps(response))
                    return
                self.fail()
                return

            #all the following operations will rely on dirid
            dirid = parsedjson['dirid']
            if "deletedir" == op:
                if dirops.deletedir(dirid, dirname, username, token):
                    self.sendLine(MSGSUCCESS)
                    return
            elif "readdir" == op:
                content = dirops.readdir(dirid, dirname, username, token)
                if content:
                    response = {}
                    response['message'] = 'success'
                    response['content'] = output
                    self.sendLine(json.dumps(response))
                    return
            elif "renamedir" == op:
                if dirops.renamedir(dirid, dirname, username, token):
                    self.sendLine(MSGSUCCESS)
                    return
            elif "permdir" == op:
                perms = parsedjson['permissions']
                if dirops.permdir(dirid, dirname, perms, username, token):
                    self.sendLine(MSGSUCCESS)
                    return


        self.fail()
        return

##
# FileServerFactor()
#
# class that will be run to set up a new fileserver instance. Kind of like a factory ;)
class FileServerFactory(Factory):
    def __init__(self):
        self.users = {} # maps user names to Chat instances

    def buildProtocol(self, addr):
        #print addr
        return FileServer(self.users)


##Main code
certData = getModule(__name__).filePath.sibling('server.pem').getContent()
certificate = ssl.PrivateCertificate.loadPEM(certData)
reactor.listenSSL(10023, FileServerFactory(), certificate.options())
reactor.run()
