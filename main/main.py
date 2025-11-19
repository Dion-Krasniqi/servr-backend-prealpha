from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from pydantic import BaseModel
from auth.models import User, DataBaseUser
from auth.methods import get_user, get_current_user, get_current_active_user

fake_users = {
        "johndoe": {
            "username":"johndoe",
            "email":"johndoe@servr.com",
            "hashed_password": "fakehashedsecret",
            "active": True,
 },}

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
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect nnname or password")
    user = DataBaseUser(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect name or password")
    
    return {"access_token": user.username, "token_type": "bearer"}
