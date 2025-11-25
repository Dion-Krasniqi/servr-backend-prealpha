from typing import Annotated
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .models import * #DataBaseUser, User 
from pwdlib import PasswordHash
from sqlalchemy import select, insert
from sqlalchemy.orm import Session, DeclarativeBase

#maybe define link to db here

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from database.database import *


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "853237eb79d57d78bbcad22b7c81f5e8e4ec8c05b8cd44905d428316e981b3d2e" # would env this but just test
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

Base.metadata.create_all(engine) # from database.py

session = Session(engine) #SessionLocal

password_hash = PasswordHash.recommended()
def verify_password(raw_password, hashed_password):
    return password_hash.verify(raw_password, hashed_password)
def get_password_hash(password):
    return password_hash.hash(password)

def get_user(username:str):
    row = session.execute(select(UserPSQL).where(UserPSQL.username == username)).first()
    if row:
        user_dict = {"username":row[0].username,
                     "email":row[0].email, 
                     "hashed_password":row[0].hashed_password, 
                     "active":row[0].active}
        return DataBaseUser(**user_dict)

def authenticate_user(username: str, password: str):
    user = get_user(username)
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

def fake_decode_token(token):
    user = get_user(token)
    return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"}
                                          )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if (current_user.active==False):
        raise HTTPException(status_code=400, detail="Inactive User")
    return current_user

async def create_new_user(username: str, email: str, password: str):
    newUser = {"username" : username, "email" : email, "hashed_password" : get_password_hash(password), "active" : True}
    session.execute(insert(UserPSQL).values(newUser))
