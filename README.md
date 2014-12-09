FyreBox
=======
{natnaelg, mchlljy, ogutu, wrv}@mit.edu

FyreBox is an encrypted file system for 6.858. 

##Installation
### Installing required libraries
OpenSSL is needed for cryptographic operations: https://www.openssl.org/ 
TwistedMatrix is used on the server side for handling multiple clients and SSL http://twistedmatrix.com/trac/

All other required libraries are located in the `requirements.txt` file. To install
them using pip, run:

    pip install -r requirements.txt

