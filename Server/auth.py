from db import *
from logging import *

import hashlib
import random
import pbkdf2

def newtoken(db, person):
    hashinput = '%s%.10f' % (person.password_hash, random.random())
    person.token = hashlib.sha256(hashinput).hexdigest()
    db.commit()
    return person.token

##
# login(username, password)
# 
# username - The username of the user
# password - The password of the user
#
# Looks up the pair in the password database (after hashing 
# the password with the salt). Then creates the token to send
# back to the user.
# 
def login(username, password):
    db = user_setup()
    person = db.query(User).get(username)

    if not person:
        return (None, None)

    hashedpass = unicode(pbkdf2.PBKDF2(password, person.salt).hexread(32), errors='replace')

    if person.password_hash == hashedpass:
        return (newtoken(db, person), person.rootdir)
    else:
        return (None, None)

##
# register(username, password)
# 
# username - The username of the user
# password - The password of the user
#
# Creates a new entry in the login database and creates
# the token like in login
#
def register(username, password):
    db = user_setup()
    person = db.query(User).get(username)

    if person:
    	print username + " person exists"
        return (None, None)

    dirdb = directory_setup()

    #now we add the person and add it to the other database
    salt = unicode(os.urandom(8), errors='replace')
    hashpass = unicode(pbkdf2.PBKDF2(password,salt).hexread(32), errors='replace')
    rootdir = hashlib.md5('%s%.10f' % (hashpass, random.random())).hexdigest()
    dirlol = db.query(Directory).get(rootdir)
    if dirlol:
        print "error creating user"
        return (None, None)

    newdir = Directory(rootdir, rootdir)
    newperson = User(username, hashpass, salt, rootdir)

    dirdb.add(newdir)
    db.add(newperson)
    dirdb.commit()
    db.commit()


    return (newtoken(db, newperson), rootdir)

def check_token(username, token):
    db = user_setup()
    person = db.query(User).get(username)
    if person and person.token == token:
        return True
    else:
        return False
