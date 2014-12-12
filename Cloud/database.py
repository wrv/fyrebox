"""database.py file

This file contains information for Public Key table installation which holds the
Public Keys for all users.
"""

from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base

# create in-memory db -- testing
engine = create_engine('sqlite:///cloud.db', echo=True) # TODO: config file ?

Base = declarative_base()
class PublicKey(Base):
    """ Stores a user's public key
            username : user's username
            pk : user's public key
    """

    __tablename__ = 'pks'
    id = Column(Integer, Sequence('public_key_seq'), primary_key=True)
    username = Column(String)
    key = Column(String(512))

    def __repr__(self):
        return "<User( username='%s', key='%s')>" % (
                self.username, self.key)


if not engine.dialect.has_table(engine.connect(), "pks"):
    # install PublicKey table if it does not exist
    Base.metadata.create_all(engine)

