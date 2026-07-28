from pydantic import BaseModel

#api key storage schema
class Api(BaseModel):
    api_key:str
    model:str
    expiry:str
    usability:str

#user schema
class User(BaseModel):
    username:str
    password:str
    email:str

#login schema
class Login(BaseModel):
    username:str                        
    password:str

