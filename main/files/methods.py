from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse

from sqlalchemy import create_engine, select, insert, func, any_, update
from sqlalchemy.orm import Session
from typing import List

from main.database.database import *
from main.auth.models import *
from .models import *

import os

storage_url = os.path.realpath(os.path.expanduser("/home/servr-api/storage"))

session = Session(engine)


async def create_file(file: UploadFile, 
                      dir_path:str, 
                      current_user: DataBaseUser,
                      client):

    owner_id = current_user.id
    # minio handles call for duplicaes 
    
    file_id = uuid.uuid4()
    object_name = dir_path + file.filename
    
    found = client.bucket_exists(bucket_name = str(owner_id))
    if not found:
        print("User bucket doesn't exist!")
        return -1
    try:
        client.put_object(
                bucket_name = str(owner_id),
                object_name = object_name,
                data = file.file,
                length = file.size,
                )
    except Exception as e:
        print("An error occurred: ", e)
        return -1

    name, extension = os.path.splitext(file.filename)
    new_file = {"file_id": file_id, 
                "filename": name, 
                "extension": extension, 
                "size": file.size, 
                "owner_id": owner_id,
                "bucket": object_name}
    
    try:
                session.execute(insert(FilePSQL).values(new_file))
                session.commit()
    
    except Exception as e:
                print(e)
                session.rollback()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=502, detail="Error occured while adding file")
    
    return object_name

async def get_files(user: DataBaseUser,
                    client):    
    owner_id = user.id 
    try:
        files = client.list_objects(bucket_name=str(owner_id))
    except Exception as e:
        print("Error occurred: ", e)
        return -1

    for file in files:
        print(file)
    return 1

async def share_file(file_id: uuid, users: List[str]):
    # think this should stay same
    if (len(users) == 0 or file_id == None):
        return
    try:
        session.execute(update(FilePSQL).where(FilePSQL.file_id == file_id).
                    values(shared_with = FilePSQL.shared_with + users))
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        return
