from fastapi import UploadFile, HTTPException
from sqlalchemy import create_engine, select, insert, func
from sqlalchemy.orm import Session

from database.database import *
from .models import *
from auth.models import *

import os

storage_url = os.path.realpath(os.path.expanduser("/home/servr-api/storage"))

session = Session(engine)


async def create_file(file: UploadFile, current_user: DataBaseUser):
    if (current_user == None):
        return

    owner_id = current_user.id
    duplicate = session.execute(select(FilePSQL.filename)
                                .where(func.concat(FilePSQL.filename, FilePSQL.extension)
                                                                == file.filename)).first()
    if (duplicate):
        print('File already exists')
        return
    
    file_path = os.path.join(storage_url, str(owner_id))
    
    file_id = uuid.uuid4()
    file_path = os.path.join(file_path, str(file_id))
    contents = await file.read()
    # potentially save file id for the filename, just keep filename in postgres
    try:
        with open(file_path, 'wb') as f:
            f.write(contents)
    except Exception as e:
        print(e)
    
    name, extension = os.path.splitext(file.filename)
     
    new_file = {"file_id": file_id, 
                "filename": name, 
                "extension": extension, 
                "size": file.size, 
                "owner_id": owner_id,}
    
    try:
                session.execute(insert(FilePSQL).values(new_file))
                session.commit()
    
    except Exception as e:
                print(e)
                session.rollback()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=502, detail="Error occured while adding file")

async def get_files(user: DataBaseUser):
    if (user == None):
        return
    owner_id = user.id
   
    file_path = os.path.join(storage_url, str(owner_id))
    
    results = session.execute(select(FilePSQL.filename, FilePSQL.extension).where(FilePSQL.owner_id == owner_id))
    for res in results:
        cur_path = os.path.join(file_path, res.filename + res.extension)
        print(cur_path)
