import os
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DEBUG_DB = False
Base = declarative_base()
FileBase = declarative_base()
PermissionBase = declarative_base()
DirectoryBase = declarative_base()


class User(Base):
	__tablename__ = "user"
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	password = Column(String(128))
	salt = Column(String(128))
	token = Column(String(128))
	permissions = relationship("Permission")
	


class Directory(Base):
	__tablename__ = "directory"
	id = Column(String(128), primary_key=True)
	dirname = Column(String(128))
	content = Column(String)
	files = relationship("File", backref="directory")


	#need to setup init and refr methods

class File(Base):
	__tablename__ = "file"
	id = Column(String(128), primary_key=True)
	filename = Column(String(128), unique=True)
	content = Column(String)
	dir_id = Column(String(128), ForeignKey("directory.id"))
	permissions = relationship("Permission", backref="file")




class Permission(Base):
	__tablename__ = "permission"
	id = Column(Integer, primary_key=True)
	file_id = Column(String(128), ForeignKey('file.id'))
	user_name = Column(String(128), ForeignKey('user.name'))
	perm_type = Column(Integer) # max should be 7 and min should be 1



	#need to setup init and refr methods

def setup_dbs(name):
	#setup jailing here

    engine = create_engine('sqlite:///%s.db' % name, echo=DEBUG_DB)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def user_setup():
    return  setup_dbs("user")

def file_setup():
    return  setup_dbs("file")

def permission_setup():
    return  setup_dbs("permission")


if __name__ == '__main__':
    cmd = raw_input('Recreate DB? (y/n) ')
    if cmd == 'y':
        user_setup()
        file_setup()
        permission_setup()
    else:
    	raise Exception("unknown command %s" % cmd)

