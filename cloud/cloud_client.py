"""cloud_client.py file

This file contains a sample cloud client. This should be added to the client
code. It's just a sample
"""

import socket
import ssl
import json
import pprint
from settings import SERVER_NAME, SERVER_PORT


connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# require a certificate from the server. Since certificate is self-generated,
# it'll be it's own authority

ssl_sock = ssl.wrap_socket(connect_socket,
        ca_certs="certs/server.crt",
        cert_reqs=ssl.CERT_REQUIRED)

ssl_sock.connect((SERVER_NAME, SERVER_PORT))

print "CONNECTED "
print "peername"
print repr(ssl_sock.getpeername())

print "cipher"
print ssl_sock.cipher()
print "certificate"
print pprint.pformat(ssl_sock.getpeercert())


# Set a simple HTTP request -- use httplib in actual code.
#ssl_sock.write("""GET / HTTP/1.0\r
        #Host: www.verisign.com\r\n\r\n""")

def write_message_from_dict(msg_dict):
    if 'operation' not in msg_dict:
        raise ValueError
    data = json.dumps(msg_dict)
    ssl_sock.write(data)

write_message_from_dict({'operation':'retrieve','user':'ogutu'})


# Read a chunk of data.  Will not necessarily
# read all the data returned by the server.
data = ssl_sock.read()

print "REPLY DATA ::::: " , data

# note that closing the SSLSocket will also close the underlying socket
ssl_sock.close()
