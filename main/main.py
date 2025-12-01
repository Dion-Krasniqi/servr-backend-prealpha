from typing import Annotated, List
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.responses import FileResponse

from minio import Minio
from minio.error import S3Error

from main.auth.methods import *
from main.auth.models import *
from main.files.methods import *
# just for rust for now
import httpx

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

minio_endpoint = "play.min.io"
minio_client = Minio(
                endpoint = minio_endpoint,
                access_key = "Q3AM3UQ867SPQQA43P2F",
                secret_key = "zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG",
                )
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
async def create_user(form: CreateUserForm):

    user_id = await create_new_user(form.username, form.email, form.password, minio_client)
    return user_id

# files ish
@app.post("/upload_file")
async def upload_file(file: UploadFile,
                      dir_path:str,
                      current_user: Annotated[DataBaseUser, Depends(get_current_active_user)]):
    if (dir_path.strip()):
        dir_path = dir_path + "/"
    new_file = await create_file(file, dir_path, current_user, minio_client)
    if (new_file):
        print("Uploaded: ", new_file)
        return 1
    else:
        print("Error")
        return -1

   # run background checks/tasks async with httpx.AsyncClient() as client:
   #     await client.post('http://127.0.0.1:3000/hello', json = {'file_name' : file.filename}) 

@app.get("/files")
async def show_files(current_user: Annotated[DataBaseUser, Depends(get_current_active_user)]):
    files = await get_files(current_user, minio_client)
    return files

@app.post("/share")
async def share_with(file: Annotated[str, Form()], emails: Annotated[str, Form()],
                     current_user: Annotated[DataBaseUser, Depends(get_current_active_user)]):
    
    emails = List[str]
    for email in emails.split(','):
        if email.strip() == current_user.email:
            continue
        emails.append(email.strip())
    
    await share_file(file, emails)
