FyreBox
=======
{natnaelg, mchlljy, ogutu, wrv}@mit.edu

FyreBox is an encrypted file system for 6.858. 

##Installation
### Installing required libraries
Need following packages

libffi-dev

libssl-dev

python-dev

OpenSSL is needed for cryptographic operations: https://www.openssl.org/ 
TwistedMatrix is used on the server side for handling multiple clients and SSL http://twistedmatrix.com/trac/

All other required libraries are located in the `requirements.txt` file. To install
them using pip, run:

    pip install -r requirements.txt

####Quick run
From the root directory, just run

    ./quick-fyrebox
###Long run
If quick-fyrebox doesn't work (we had some issues) do the following in 3
different shells.

cd Server

python server.py

cd Cloud

python server.py

cd Client

python client.py
