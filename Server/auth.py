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
    person = db.query(User).filter(User.name == username).first()

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
    person = db.query(User).filter(User.name == username).first()

    if person:
    	print username + " person exists"
        return (None, None)

    filedb = file_setup()
    permdb = permission_setup()

    #now we add the person and add it to the other database
    salt = unicode(os.urandom(8), errors='replace')
    hashpass = unicode(pbkdf2.PBKDF2(password,salt).hexread(32), errors='replace')
    rootdir = hashlib.md5('%s%.10f' % (hashpass, random.random())).hexdigest()
    dirlol = db.query(File).filter(File.filename == rootdir).first()
    if dirlol:
        print "error creating user"
        return (None, None)

    newperson = User(name=username, password_hash=hashpass, salt=salt, rootdir=rootdir)
    newdir = File(identifier=rootdir, filename=rootdir, owner_id=newperson.id, content="", directory=True)


    filedb.add(newdir)
    db.add(newperson)
    filedb.commit()
    db.commit()
    
    newperm = Permission_Assoc(user_id=newperson.id, file_id=newdir.id, perm_type=True)
    permdb.add(newperm)
    permdb.commit()
    return (newtoken(db, newperson), rootdir)

def check_token(username, token):
    db = user_setup()
    person = db.query(User).filter(User.name == username).first()
    if person and person.token == token:
        return True
    else:
        return False
