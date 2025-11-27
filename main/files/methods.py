from fastapi import UploadFile
from sqlalchemy import create_engine, select, insert
from sqlalchemy.orm import Session

from database.database import *
from .models import *
from auth.models import *

import os

storage_url = os.path.realpath(os.path.expanduser("/home/servr-api/storage"))

session = Session(engine)


async def create_file(file: UploadFile, current_user: DataBaseUser):
    owner_id = str(current_user.id)
    file_path = os.path.join(storage_url, owner_id)
    file_path = os.path.join(file_path, file.filename)
    contents = await file.read()
    try:
        with open(file_path, 'wb') as f:
            f.write(contents)
    except Exception as e:
        print(e)
    
    ## check for bucket and stuff
    ## write to database
