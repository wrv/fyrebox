from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


UserBase = declarative_base()
FilesBase = declarative_base()
PermissionBase = declarative_base()

class User(UserBase):
	__tablename__ = "user"
	id = Column(Integer, primary_key=True)
	username = Column(String, unique=True)
	password = Column(String(128))
	token = Column(String(128))


class File(FilesBase):
	__tablename__ = "file"
	id = Column(Integer, primary_key=True)
	filename = Column(String(128))
	owner_id = Column(ForeignKey('user.id'))
	content = Column(String)
	key = Column(String)



class Permission(PermissionBase):
	__tablename__ = "permission"
	id = Column(Integer, primary_key=True)
	file_id = Column(ForeignKey('file.id'))
	user_id = Column(ForeignKey('user.id'))
	perm_type = Column(Integer) # max should be 7 and min should be 1