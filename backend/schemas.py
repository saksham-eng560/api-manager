from pydantic import BaseModel


class Api(BaseModel):
    api_key: str
    model: str
    expiry: str
    usability: str


class User(BaseModel):
    username: str
    password: str
    email: str


class Login(BaseModel):
    username: str
    password: str
