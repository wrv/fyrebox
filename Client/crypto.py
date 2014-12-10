from Crypto.Cipher import AES
import base64
import os
import time
from OpenSSL import SSL
import socket
import json

def encrypt(content, key):
        BLOCK_SIZE = 32
	PADDING = '{'
        pad = lambda s: s + (BLOCK_SIZE - (len(s) % BLOCK_SIZE)) * PADDING
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        cipher = AES.new(key)
        encoded = EncodeAES(cipher,content);
        return encoded
def decrypt(content, key):
        PADDING = "{"
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
        encryption = content
        cipher = AES.new(key)
        decoded = DecodeAES(cipher, encryption)
        return decoded
