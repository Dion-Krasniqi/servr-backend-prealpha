from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel
from auth.models import User, DataBaseUser, Token
from auth.methods import * #get_user, get_current_user, get_current_active_user
from database import *

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import select

fake_users = {
        "johndoe": {
            "username":"johndoe",
            "email":"johndoe@servr.com",
            "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$DPSn4ZmyAQCE/xecn01Q7Q$T6t3QcgODCWTTgzCfuVXtcUDal71bWv16exqpFTO49k",
            "active": True,
 },}

class Base(DeclarativeBase):
    pass

class User1(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str]
    hashed_password: Mapped[str]
    active: Mapped[bool]


Base.metadata.create_all(engine)

with Session(engine) as session:
    row = session.execute(select(User1))
    for res in row.scalars():
            print(res.username)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_hash_password(password: str):
    return "fakehashed" + password

@app.get("/")
async def root():
   return {"message":"Hello World"}
@app.get("/items/")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
@app.get("/passi")
async def hash_it():
    # since havent made create account point
    return get_password_hash("secret")
@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()])->Token:
    user = authenticate_user(fake_users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, 
                            detail="Incorrect name or password", 
                            headers={"WWW-Authenticate": "Bearer"},
                            )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
            data={"sub":user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
    
