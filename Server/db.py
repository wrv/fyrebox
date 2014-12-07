import os

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DEBUG_DB = False
UserBase = declarative_base()
FileBase = declarative_base()
PermissionBase = declarative_base()


class User(UserBase):
	__tablename__ = "user"
	#id = Column(Integer, primary_key=True)
	username = Column(String, unique=True, primary_key=True)
	password = Column(String(128))
	salt = Column(String(128))
	token = Column(String(128))

	#need to setup init and refr methods

class File(FileBase):
	__tablename__ = "file"
	id = Column(Integer, primary_key=True)
	filename = Column(String(128))
	owner_id = Column(ForeignKey('user.id'))
	content = Column(String)

	#need to setup init and refr methods

class Permission(PermissionBase):
	__tablename__ = "permission"
	id = Column(Integer, primary_key=True)
	file_id = Column(ForeignKey('file.id'))
	user_id = Column(ForeignKey('user.id'))
	perm_type = Column(Integer) # max should be 7 and min should be 1

	#need to setup init and refr methods

def setup_dbs(name, base):
	#setup jailing here

    engine = create_engine('sqlite:///%s.db' % name, echo=DEBUG_DB)
    base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def user_setup():
    return  setup_dbs("user", UserBase)

def file_setup():
    return  setup_dbs("file", FileBase)

def permission_setup():
    return  setup_dbs("permission", PermissionBase)


if __name__ == '__main__':
    cmd = raw_input('Recreate DB? (y/n) ')
    if cmd == 'y':
        user_setup()
        file_setup()
        permission_setup()
    else:
    	raise Exception("unknown command %s" % cmd)

