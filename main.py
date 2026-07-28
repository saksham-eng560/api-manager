from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import ApiKey, User_data, session
from auth import verify_token, password_hash, verify_password, create_access_token
from schemas import User,Api
from typing import Annotated
from crypter import encrypt, decrypt
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@app.post("/login")
def verify_user(user_details: OAuth2PasswordRequestForm = Depends()):
    stored_user = session.query(User_data).filter(User_data.username == user_details.username).first()
    if stored_user and verify_password(user_details.password, stored_user.password):
        token = create_access_token(data={"username": stored_user.username, "email": stored_user.email})
        # OAuth2PasswordBearer/Swagger UI reads these standard field names and
        # then sends `Authorization: Bearer <access_token>` for locked routes.
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")


@app.post("/signup")
def create_user(new_user: User):
    if session.query(User_data).filter(User_data.username == new_user.username).first():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username already exists")
    hashed_password = password_hash(new_user.password)
    insert_user = User_data(username=new_user.username, password=hashed_password, email=new_user.email)
    try:
        session.add(insert_user)
        session.commit()
    except Exception:
        session.rollback()
        raise
    return {"message": "User created successfully, Now you can login"}


@app.get("/home")
def home(current_user: Annotated[dict, Depends(verify_token)]):
    user = session.query(User_data).filter(User_data.username == current_user["username"]).first()
    all_keys = session.query(ApiKey).filter(ApiKey.userid == user.userid).all()
    # Do not assign the decrypted value onto an ORM object.  Doing so marks it
    # dirty and a later request can accidentally save the plaintext key.
    api_keys = [
        {
            "api_id": key.api_id,
            "api_key": decrypt(key.api_key),
            "model": key.model,
            "expiry": key.expiry,
            "usability": key.usability,
        }
        for key in all_keys
    ]
    return {"message": "Welcome to API Key Manager", "api_keys": api_keys}


@app.post("/new")
def new(new_api_key: Api, current_user: Annotated[dict, Depends(verify_token)]):
    user = session.query(User_data).filter(User_data.username == current_user["username"]).first()
    crypted_key = encrypt(new_api_key.api_key)
    api_key_record = ApiKey(
        userid=user.userid,
        api_key=crypted_key,
        model=new_api_key.model,
        expiry=new_api_key.expiry,
        usability=new_api_key.usability
    )
    session.add(api_key_record)
    session.commit()
    return {"message": "API Key created successfully", "api_id": api_key_record.api_id}


@app.delete("/delete/{given_api_id}")
def delete(given_api_id: int, current_user: Annotated[dict, Depends(verify_token)]):
    user = session.query(User_data).filter(User_data.username == current_user["username"]).first()
    deleted = session.query(ApiKey).filter(ApiKey.api_id == given_api_id,ApiKey.userid == user.userid).delete()
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    session.commit()
    return {"message": "API Key deleted successfully"}
