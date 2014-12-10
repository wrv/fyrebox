import os
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String, Boolean, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DEBUG_DB = False
Base = declarative_base()


class User(Base):
	__tablename__ = "user"
	id = Column(Integer, primary_key=True)
	name = Column(String, unique=True)
	password_hash = Column(String(128))
	salt = Column(String(128))
	token = Column(String(128))
	rootdir = Column(String(128), default="/")
	permissions = relationship('Permission_Assoc')
	files = relationship('File')


class File(Base):
	__tablename__ = "file"
	id = Column(Integer, primary_key=True)
	identifier = Column(String, unique=True)
	filename = Column(String(128), unique=True)
	parent_id = Column(Integer, ForeignKey("file.id"))
	owner_id = Column(Integer, ForeignKey("user.id"))
	content = Column(String)
	directory = Column(Boolean)
	permissions = relationship('Permission_Assoc')
	sub_directories = relationship('File')


class Permission_Assoc(Base):
	__tablename__ = "permission_assoc"
	user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
	file_id = Column(Integer, ForeignKey('file.id'), primary_key=True)
	perm_type = Column(Boolean) # true = read&write, false = read

	user = relationship('User')




def setup_dbs(name):
	#setup jailing here

    engine = create_engine('sqlite:///%s.db' % name, echo=DEBUG_DB)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    return Session()

def user_setup():
    return  setup_dbs("user")

def file_setup():
    return  setup_dbs("file")

def permission_setup():
    return  setup_dbs("permission_assoc")




if __name__ == '__main__':
        user_setup()
        file_setup()
        permission_setup()


