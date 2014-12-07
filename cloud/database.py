"""database.py file

This file contains information for Public Key table installation which holds the
Public Keys for all users.
"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# create in-memory db -- testing
engine = create_engine('sqlite:///:memory:', echo=True) # TODO: config file ?

Base = declarative_base()
class PublicKey(Base):
    """ Stores a user's public key
            username : user's username
            pk : user's public key
    """
    # TODO: add VARCHAR length for non-sqlite dbs e.g Column(String(50))

    __tablename__ = 'pks'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    pk = Column(String)

    def __repr__(self):
        return "<User(id='%d', username='%s', pk='%s')>" % (
                self.id, self.username, self.pk)


if not engine.dialect.has_table(engine.connect(), "pks"):
    # install PublicKey table if it does not exist
    Base.metadata.create_all(engine)

