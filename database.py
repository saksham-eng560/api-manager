from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, MetaData
from dotenv import load_dotenv
import os
from uuid import uuid4

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
meta = MetaData()
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


class User_data(Base):
    __tablename__ = "user_info"
    # Generate the identifier when a new User_data object is inserted, so
    # /signup never has to accept or provide a user id.
    userid = Column(String(36), primary_key=True, unique=True, nullable=False,
                    default=lambda: str(uuid4()))
    username = Column(String,nullable=False)
    password = Column(String)
    email = Column(String)
    api_keys = relationship("ApiKey", back_populates="user")


class ApiKey(Base):
    __tablename__ = "api_key"
    # An API key needs its own primary key; userid is the ownership foreign key
    # and may occur many times (one user can store multiple API keys).
    api_id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(String(36), ForeignKey("user_info.userid", ondelete="CASCADE"), nullable=False, index=True)
    api_key = Column(String, nullable=False)
    model = Column(String)
    expiry = Column(String)
    usability = Column(String)
    user = relationship("User_data", back_populates="api_keys")


Base.metadata.create_all(engine)

