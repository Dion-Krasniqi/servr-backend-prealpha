from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, List
from pydantic import BaseModel
from auth.methods import *
from auth.models import *

from files.methods import *


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
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, 
                            detail="Incorrect email or password", 
                            headers={"WWW-Authenticate": "Bearer"},
                            )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
            data={"sub":user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
@app.post("/create_user")
async def create_user(username: Annotated[str, Form()], email: Annotated[str, Form()],
                      password:Annotated[str, Form()]):

  await create_new_user(username,email,password)
  return 0 

# files ish
@app.post("/upload_file")
async def upload_file(file: UploadFile, current_user: Annotated[DataBaseUser, Depends(get_current_active_user)]):
     await create_file(file, current_user)

@app.get("/files")
async def show_files(current_user: Annotated[DataBaseUser, Depends(get_current_active_user)]):
    await get_files(current_user)

@app.post("/share")
async def share_with(file: Annotated[str, Form()], emails: Annotated[str, Form()]):
    emails = [email.strip() for email in emails.split(',')]
    
    await share_file(file, emails)
