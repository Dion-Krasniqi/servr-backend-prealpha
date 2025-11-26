import jwt
import uuid
import os

from dotenv import load_dotenv
from typing import Annotated
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select, insert, create_engine
from sqlalchemy.orm import Session

from database.database import *
from .models import * #DataBaseUser, User 


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

load_dotenv()
storage_url = os.getenv("STORAGE_ADDRESS")
SECRET_KEY = "853237eb79d57d78bbcad22b7c81f5e8e4ec8c05b8cd44905d428316e981b3d2e" # env this soon
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

session = Session(engine) 

password_hash = PasswordHash.recommended()

def verify_password(raw_password, hashed_password):
    return password_hash.verify(raw_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)

def get_user(email:str):
    row = session.execute(select(UserPSQL).where(UserPSQL.email == email)).first()
    if row:
        user_dict = {"username":row[0].username,
                     "email":row[0].email, 
                     "hashed_password":row[0].hashed_password, 
                     "active":row[0].active,
                     "id":row[0].id}
        return DataBaseUser(**user_dict)

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"}
                                          )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if (current_user.active==False):
        raise HTTPException(status_code=400, detail="Inactive User")
    return current_user

async def create_new_user(username: str, email: str, password: str):
    user = get_user(email)
    if user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    new_id = uuid.uuid4()
    newUser = {"username" : username, "email" : email, "hashed_password" : get_password_hash(password), "active" : True, "id": new_id}
    try:
        session.execute(insert(UserPSQL).values(newUser))
        session.commit()
        #create directory
    except:
        session.rollback()
        raise HTTPException(status_code=502, detail="Error occured while creating user")
    return 1
