from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, create_engine

import datetime

from config import DATABASE_URI

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
SESSION = Session()

Base = declarative_base()

class Recomendation(Base):
    __tablename__ = 'recomendations'
    id = Column(Integer(), primary_key = True)
    parent_id = Column(Integer())
    url = Column(String(255),)
    file = Column(String(255),)
    data = Column(DateTime, default=datetime.datetime.utcnow)
    #page_source = Column(Text,)
    visited  = Column(Integer())