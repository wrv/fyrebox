import os
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DEBUG_DB = False
Base = declarative_base()


class User(Base):
	__tablename__ = "user"
	name = Column(String, unique=True)
	password = Column(String(128))
	salt = Column(String(128))
	token = Column(String(128))
	
	def __init__(self, name, password, salt, token):
		self.name = name
		self.salt = salt
		self.token = token

class Directory(Base):
	__tablename__ = "directory"
	id = Column(String(128), primary_key=True)
	key = Column(String(128))
	dirname = Column(String(128))
	content = relationship("File", backref="directory")

	def __init__(self, id, key, dirname, content):
		self.id = id
		self.key = key
		self.dirname = dirname
		self.content = content

class File(Base):
	__tablename__ = "file"
	id = Column(String(128), primary_key=True)
	key = Column(String)
	filename = Column(String(128), unique=True)
	content = Column(String)
	dir_id = Column(String(128), ForeignKey("directory.id"))
	users_write = relationship("Permission", backref="file", primaryjoin="permission.perm_type == True")
	users_read = relationship("Permission", backref="file", primaryjoin="permission.perm_type == False")

	def __init__(self, id, key, filename, content, dir_id, users_write, users_read):
		self.id = id
		self.key = key
		self.filename = filename
		self.content = content
		self.dir_id = dir_id
		self.users_write = users_write
		self.users_read = users_read



class Permission(Base):
	__tablename__ = "permission"
	id = Column(Integer, primary_key=True)
	file_id = Column(String(128), ForeignKey('file.id'))
	user_name = Column(String(128), ForeignKey('user.name'))
	perm_type = Column(Boolean) # true = read&write, false = read

	def __init__(self, id, perm_type, user_name, file_id):
		self.id = id
		self.file_id = file_id
		self.perm_type = perm_type
		self.user_name = user_name


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
        user_setup()
        file_setup()
        permission_setup()


