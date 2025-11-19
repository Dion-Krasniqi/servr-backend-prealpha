from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .models import DataBaseUser, User 

#maybe define link to db here
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user(db, username:str):
    if username in db:
        user_dict = db[username]
        return DataBaseUser(**user_dict)

def fake_decode_token(db, token):
    user = get_user(db,token)
    return user

async def get_current_user(db, token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(db,token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentals",
                            headers={"WWW-Authenticate":"Bearer"},
                            )
    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if (current_user.active==False):
        raise HTTPException(status_code=400, detail="Inactive User")
    return current_user
