"""database.py file

This file contains information for Public Key table installation which holds the
Public Keys for all users.
"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# create in-memory db
engine = create_engine('sqlite:///:memory:', echo=True) # TODO: config file ?

Base = declarative_base()
class PublicKey(Base):
    __tablename__ = 'pks'

    id = Column(Integer, primary_key=True)
    # TODO: add VARCHAR length for non-sqlite dbs e.g Column(String(50))
    username = Column(String)
    pk = Column(String) # raw public key value

    def __repr__(self):
        return "<User(id='%d', username='%s', pk='%s')>" % (
                self.id, self.username, self.pk)


if not engine.dialect.has_table(engine.connect(), "pks"):
    # install PublicKey table
    Base.metadata.create_all(engine)

