import json, os

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, ssl
from twisted.python.modules import getModule

from settings import  FILE_SERVER_PORT

from auth import login, register
import fileops
import dirops
import time
import logger
from logger import log
#import log_client


#Organization of all our operations for authentication, files, and directory
AUTHOPS = ['register', 'login']
FILEOPS = ['create', 'delete', 'read', 'write', 'rename', 'perm']
DIROPS = ['createdir', 'deletedir', 'readdir', 'writedir', 'renamedir', 'permdir']

#Fail and success messages to respond to the client with
MSGFAIL = '{"message":"failure"}'
MSGSUCCESS = '{"message":"success"}'

#for logging purposes
curfile = 'server.py'

##
# FileServer(lineReceiver)
#
# Class that handles each connection
class FileServer(LineReceiver):

    def __init__(self):
        self.state = "UNAUTHENTICATED"
        self.user = None

    ##
    # connectionMade()
    #
    # Run whenever the initial condition is made with the server
    def connectionMade(self):
        self.sendLine('{"message":"connected"}')

    ##
    # connectionLost(reason)
    #
    # Run whenever the connection is lost with a client
    def connectionLost(self, reason):
        log(curfile, "connection lost with client. reason: " + str(reason))
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
            username = parsedjson['username']
            password = parsedjson['password']
        except:
            print "error in json. msg: " + message
            return

        token = None
        rootdir = None

        if op not in AUTHOPS:
            self.fail()
            return

        if "register" == op:
            log(curfile, "registering")
            (token, rootdir) = register(username, password)

        if "login" == op:
            log(curfile, "logging in user " + username)
            (token, rootdir) = login(username, password)

        
        if token:
            if rootdir:
                log(curfile, "token successful for user: " + username)
                self.user = username
                response = {}
                response['username'] = username
                response['token'] = token
                response['timestamp'] = time.time()
                response['rootdir'] = rootdir
                self.sendLine(json.dumps(response))
                self.state = "AUTHENTICATED"
        else:
            log(curfile, "token unsuccessful for user: " + username)
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
            log(curfile, "error parsing " + self.user + " json or operation: " + message)
            self.fail()
            return

        if op not in FILEOPS and op not in DIROPS:
            log(curfile, "error parsing " + self.user + " json operation: " + message)
            self.fail()
            return

        try:
            username = parsedjson['username']
            token = parsedjson['token']
        except:
            log(curfile, "error parsing json username " + self.user + " or token: " + message)
            self.fail()
            return

        #### File Operations
        if op in FILEOPS:
            try:
                filename = parsedjson['filename']
            except:
                log(curfile, "error parsing " + username + " json filename: " + message)
                self.fail()
                return

            if "create" == op:
                try:
                    dirname = parsedjson['dirname']
                except:
                    log(curfile, "error parsing json dirname: " + message)
                    self.fail()
                    return

                output = fileops.create(filename, dirname, username, token)
                if output:
                    log(curfile, "successfully created file for user " + username)
                    self.sendLine(json.dumps(output))
                    return
                log(curfile, "error creating file for user " + username)
                self.fail()
                return

            #All following operations will rely on the fileid
            try:
                fileid = parsedjson['fileid']
            except:
                log(curfile, "error parsing " + self.user + " json fileid: " + message)
                self.fail()
                return

            if "delete" == op:
                if fileops.delete(fileid, filename, username, token):
                    log(curfile, "successfully deleted fileid " + fileid + " for user " + username)
                    self.sendLine(MSGSUCCESS)
                    return

            elif "read" == op:
                output = fileops.read(fileid, filename, username, token)
                if False != output:
                    log(curfile, "successfully read fileid " + fileid + " for user " + username)
                    self.sendLine(json.dumps(output))
                    return

            elif "write" == op:
                try:
                    content = parsedjson['content']
                except:
                    log(curfile, "error parsing content for " + self.user + " json content: " + message)
                    self.fail()
                    return

                output = fileops.write(fileid, filename, content, username, token)
                if False != output:
                    log(curfile, "successfully wrote to fileid " + fileid + " for user " + username)
                    self.sendLine(json.dumps(output))
                    return

            elif "rename" == op:
                if fileops.rename(fileid, filename, username, token):
                    log(curfile, "successfully renamed fileid " + fileid + " for user " + username)
                    self.sendLine(MSGSUCCESS)
                    return

            elif "perm" == op:
                try:
                    perms = parsedjson['permissions']
                except:
                    log(curfile, "error parsing permissions for " + self.user + " json: " + message)
                    self.fail()
                    return

                output = fileops.perm(fileid, filename, perms, username, token)
                if output:
                    log(curfile, "successfully changed permissions for fileid " + fileid + " for user " + username)
                    self.sendLine(json.dumps(output))
                    return

        #### Directory Operations
        if op in DIROPS:
            try:
                dirname = parsedjson['dirname']
            except:
                log(curfile, "error parsing " + self.user + " json dirname: " + message)
                self.fail()
                return

            if "createdir" == op:
                parent_dir = parsedjson['parentdir']
                output = dirops.createdir(dirname, parent_dir, username, token)
                if output:
                    log(curfile, "successfully created directory for user " + username)
                    self.sendLine(json.dumps({'message':'success',
                                              'data': output}))
                    return
                log(curfile, "error creating directory for user " + username)
                self.fail()
                return

            #all the following operations will rely on dirid
            try:
                dirid = parsedjson['dirid']
            except:
                log(curfile, "error parsing " + self.user + " json dirid: " + message)
                self.fail()
                return

            if "deletedir" == op:
                if dirops.deletedir(dirid, dirname, username, token):
                    log(curfile, "successfully deleted dirid " + dirid + " for user " + username)
                    self.sendLine(MSGSUCCESS)
                    return

            elif "readdir" == op:
                output = dirops.readdir(dirid, dirname, username, token)
                if output:
                    log(curfile, "successfully read dirid " + dirid + " for user " + username)
                    self.sendLine(json.dumps(output))
                    return

            elif "renamedir" == op:
                if dirops.renamedir(dirid, dirname, username, token):
                    log(curfile, "successfully renamed dirid " + dirid + " for user " + username)
                    self.sendLine(MSGSUCCESS)
                    return
            elif "permdir" == op:
                try:
                    perms = parsedjson['permissions']
                except:
                    log(curfile, "error parsing " + self.user + " json permissions: " + message)
                    self.fail()
                    return

                if dirops.permdir(dirid, dirname, perms, username, token):
                    log(curfile, "successfully changed permissions for dirid " + dirid + " for user " + username)
                    self.sendLine(MSGSUCCESS)
                    return

        log(curfile, "error parsing json " + message + " for user " + self.user)
        self.fail()
        return

##
# FileServerFactor()
#
# class that will be run to set up a new fileserver instance. Kind of like a factory ;)
class FileServerFactory(Factory):

    def buildProtocol(self, addr):
        log(curfile,"Client connected from: " + str(addr))
        return FileServer()


##Main code
logger.main()
certData = getModule(__name__).filePath.sibling('server.pem').getContent()
certificate = ssl.PrivateCertificate.loadPEM(certData)
reactor.listenSSL(10023, FileServerFactory(), certificate.options())

def cls():
    os.system(['clear','cls'][os.name == 'nt'])

# now, to clear the screen
cls()


intro = """
                                                                                                
;kkkkkkkk,  okk.    dkk .kkkkkkkkkkkkc  ckkkkkkkk..WWWWWWWWWWW:   lWWWWWWWWWWWl  0WW.    KWN     
;kkl'''''.  oOk.    dkk  :kkd''''':kkl  ckkc'''''  :WMW::::0MM:   lMMO:::::OMMl  KMM.    XMW     
;kkc.....   oOk.    dkk  .kko.....;kkl  ckO:.....   NMN''''kMMo.  lMMd     dMMl  OMMx:',oWMK     
;kkkkkkkk;  oOk.    dkk  .kkkkkkkkkkkl  ckkkkkkkk.  NMMMMMMMMMMK  lMMd     dMMl   ,0MMMMMK;      
;kkc.....   oOkdddddkkk  .kko...dkkl.   ckO;.....   NMN.....'MMK  lMMd     dMMl  0MMd,.'lWMN     
;kk:        ,;;;;;;;xkk  .kkl    okkc   ckkl;;;;;   NMWllllloMMK  lMM0lllll0MMl  KMM.    XMW     
,xx;                xkd  .xxc     lkkl  :xxxxxxxx.  KXXXXXXXXXXO  cXXXXXXXXXXXc  OXX.    0XK     
                 .dkd             ckx.                                                          
                .xko               .                                                            
                 ';                                                                             
                                                                                                

"""
print intro
print "Server is running"
log(curfile, "Server is up and running! :D")
reactor.run()
