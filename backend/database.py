import os
from uuid import uuid4

from dotenv import load_dotenv
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User_data(Base):
    __tablename__ = "user_info"

    userid = Column(
        String(36),
        primary_key=True,
        unique=True,
        nullable=False,
        default=lambda: str(uuid4()),
    )
    username = Column(String, nullable=False)
    password = Column(String)
    email = Column(String)
    api_keys = relationship("ApiKey", back_populates="user")


class ApiKey(Base):
    __tablename__ = "api_key"

    api_id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(
        String(36),
        ForeignKey("user_info.userid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    api_key = Column(String, nullable=False)
    model = Column(String)
    expiry = Column(String)
    usability = Column(String)
    user = relationship("User_data", back_populates="api_keys")


Base.metadata.create_all(engine)
