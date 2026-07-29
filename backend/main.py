from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles

from .auth import create_access_token, password_hash, verify_password, verify_token
from .crypter import decrypt, encrypt
from .database import ApiKey, User_data, session
from .schemas import Api, User


app = FastAPI(title="API Key Manager")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/login")
def verify_user(user_details: OAuth2PasswordRequestForm = Depends()):
    stored_user = session.query(User_data).filter(User_data.username == user_details.username).first()
    if stored_user and verify_password(user_details.password, stored_user.password):
        token = create_access_token(
            data={"username": stored_user.username, "email": stored_user.email}
        )
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
    )


@app.post("/signup")
def create_user(new_user: User):
    if session.query(User_data).filter(User_data.username == new_user.username).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Username already exists"
        )
    insert_user = User_data(
        username=new_user.username,
        password=password_hash(new_user.password),
        email=new_user.email,
    )
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
        usability=new_api_key.usability,
    )
    session.add(api_key_record)
    session.commit()
    return {"message": "API Key created successfully", "api_id": api_key_record.api_id}


@app.delete("/delete/{given_api_id}")
def delete(given_api_id: int, current_user: Annotated[dict, Depends(verify_token)]):
    user = session.query(User_data).filter(User_data.username == current_user["username"]).first()
    deleted = (
        session.query(ApiKey)
        .filter(ApiKey.api_id == given_api_id, ApiKey.userid == user.userid)
        .delete()
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    session.commit()
    return {"message": "API Key deleted successfully"}


@app.get("/app", include_in_schema=False)
def frontend_app():
    return FileResponse(FRONTEND_DIR / "index.html")


# Keep this mount last so API routes and /docs are handled first.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
