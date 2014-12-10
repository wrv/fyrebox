"""database.py file

This file contains information for FileInfo table which holds the
unique file information and keys for each file
"""

from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base

# create in-memory db -- testing
engine = create_engine('sqlite:///:memory:', echo=True) # TODO: config file ?

Base = declarative_base()
class FileInfo(Base):
    """ Stores a user's public key
            username : user's username
            pk : user's public key
    """

    __tablename__ = 'filekeys'
    id = Column(Integer, Sequence('file_seq')) #, primary_key=True)
    file_name = Column(String)
    unique_id = Column(Integer, primary_key=True)
    file_key = Column(String(32))

    def __repr__(self):
        return "<User( unique_id='%d', file_name='%s',  key='%s')>" % (
                self.unique_id, self.file_name, self.file_key)


if not engine.dialect.has_table(engine.connect(), "filekeys"):
    # install FileInfo table if it does not exist
    Base.metadata.create_all(engine)

