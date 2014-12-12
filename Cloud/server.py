import json
import time

from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, ssl
from twisted.python.modules import getModule

from settings import  CLOUD_SERVER_PORT
from database import PublicKey, engine
from sqlalchemy.orm import sessionmaker

from settings import *

Session = sessionmaker(bind=engine) # session class
dbsession = Session() # TODO change to class, one session per connection



#Fail and success messages to respond to the client with
MSGFAIL = '{"message":"failure"}'
MSGSUCCESS = '{"message":"success"}'

##
# FileServer(lineReceiver)
#
# Class that handles each connection
class FileServer(LineReceiver):

    def __init__(self, users):
        self.DEBUG = True

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
        pass

    ##
    # dataReceived(data)
    #
    # Runs after connection is made and data is sent to the server
    def dataReceived(self, data):
        #print data
        self.handle_UNAUTHENTICATED(data)

    ##
    # lineReceived(line)
    #
    # Runs after connection is made and data is sent to the server
    def lineReceived(self, line):
        #print line
        self.handle_UNAUTHENTICATED(line)

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
    def handle_UNAUTHENTICATED(self, data):
        print "process_data:", data
        data = self.cleanup(data)
        if data is None: return False
        operation = data['operation'].lower()

        if operation == 'store':
            if ('username' not in data) or ('key' not in data):
                self.sendLine("Store requires username and key fields\r\n")
                return False

            successful = self.store(data['username'], data['key'])
            if successful:
                self.sendLine("OK")
            else:
                self.sendLine("FAILED")

            return False

        elif operation == 'retrieve':
            if 'username' not in data:
                self.sendLine("Retrieve requires username field\r\n")
                return False

            key = self.retrieve(data['username'])
            if key is None:
                self.sendLine("User not found")
            else:
                self.sendLine(key)
            return False

        elif operation == 'list':
            # only for debug
            if self.DEBUG:
                self.sendLine(str(list()))
                return False

        self.sendLine("OPERATION NOT SUPPORTED")

        return False # finished with client

    @staticmethod
    def cleanup(data):
        """Cleans received information and returns a cleaned-up dictionary"""
        data = data.strip()
        # make sure data is json
        try:
            data_dict = json.loads(data)
        except:
            print ":ERROR "
            return None

        if not isinstance(data_dict, dict):
            return None

        if 'operation' not in data_dict:
            return None

        return data_dict

    @staticmethod
    def store(username_, key_):
        """If username is not in database, adds key and username to public key database"""
        try:
            pub_key = PublicKey(username=username_, key=key_)
            dbsession.add(pub_key)
            dbsession.commit()
            return True
        except:
            return False

    @staticmethod
    def list():
        """ For debugging purposes only.
        Lists all keys in db"""
        time.sleep(10)
        return dbsession.query(PublicKey).all()

    @staticmethod
    def retrieve(username_):
        """If username is in database, returns saved public key. None otherwise"""
        try:
            user = dbsession.query(PublicKey).filter_by(username=username_).first()
            return user
        except:
            return None

        

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

reactor.listenSSL(CLOUD_SERVER_PORT, FileServerFactory(), certificate.options())
reactor.run()
