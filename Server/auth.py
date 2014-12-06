from db import *
from logging import *

import hashlib
import random
import pbkdf2

def newtoken(db, person):
    hashinput = "%s%s" % (person.password, os.urandom(10))
    person.token = hashlib.md5(hashinput).hexdigest()
    db.commit()
    return person.token

def login(username, password):
    db = user_setup()
    person = db.query(User).get(username)

    #We will allow people to know which users exist, so we allow this timing attack
    if not person:
        return None

    hashedpass = unicode(pbkdf2.PBKDF2(password, person.salt).hexread(32), errors='replace')

    if person.password == hashedpass:
        return newtoken(db, person)
    else:
        return None

def register(username, password):
    db = user_setup()
    person = db.query(User).get(username)

    if person:
        return None

    newperson = User()
    newperson.username = username

    #now we add the person and add it to the other database
    salt = unicode(os.urandom(8), errors='replace')
    hashpass = unicode(pbkdf2.PBKDF2(password,salt).hexread(32), errors='replace')
    newperson.password = hashpass
    newperson.salt = salt
    db.add(newperson)
    db.commit()

    return newtoken(db, newperson)

def check_token(username, token):
    db = user_setup()
    person = db.query(User).get(username)
    if person and person.token == token:
        return True
    else:
        return False