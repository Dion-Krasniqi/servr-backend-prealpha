from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse

from sqlalchemy import create_engine, select, insert, func, any_, update
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from main.database.database import *
from main.auth.models import *
from .models import *

import os
import io
storage_url = os.path.realpath(os.path.expanduser("/home/servr-api/storage"))

session = Session(engine)

FILE_TYPE = {
        "image": "media",
        "video": "media",
        "audio": "media",
        "text": "document",
        "application": "document",
}

def get_type(content_type:str):
    if not content_type:
        return "other"
    main = content_type.split("/")[0]

    return FILE_TYPE.get(main, "other")

async def create_file(file: UploadFile, 
                      dir_path:str, 
                      current_user: DataBaseUser,
                      client):

    
    owner_id = current_user.id
    found = client.bucket_exists(bucket_name = str(owner_id))
    if not found:
        print("User bucket doesn't exist!")
        return -1
    
    file_id = uuid.uuid4()
    
    # object_name = file.filename.replace(" ", "_")
    
    # think about this
    name, extension = os.path.splitext(file.filename)
    object_name = str(file_id) + extension

    c = await file.read()
    length = len(c)
    content_type = get_type(file.content_type)
    try:
        client.put_object(
                bucket_name = str(owner_id),
                object_name = object_name,
                data = io.BytesIO(c),
                length = length,
                content_type = content_type 
                )
    except Exception as e:
        print("An error occurred: ", e)
        return -1
    new_file = {"file_id": file_id, 
                "filename": name, 
                "extension": extension, 
                "size": file.size, 
                "owner_id": owner_id,
                "type": content_type,
                "createdat": "1970-01-01",
                "lastmodified": "1970-01-01",
                "url":"url1"}
    try:
                session.execute(insert(FilePSQL).values(new_file))
                session.commit()
    
    except Exception as e:
                print(e)
                session.rollback()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise HTTPException(status_code=502, detail="Error occured while adding file")
    
    return file.filename

async def get_files(user: DataBaseUser,
                    client,
                    queries: List[str] | None = None,
                    directory: uuid.UUID | None = None,
                    ):    
    owner_id = user.id

    stmt = select(FilePSQL).where(FilePSQL.owner_id == owner_id)
    if (directory):
        stmt = stmt.where(FilePSQL.folder_id == directory)
    if (queries):
        stmt = stmt.where(FilePSQL.type == queries[0])
    try:

        files = session.execute(stmt).scalars().all()
        #files = client.list_objects(bucket_name=str(owner_id))
    except Exception as e:
        print("Error occurred: ", e)
        return -1
    print(files)
    documents = []
    for file in files:
        # not like this tbh
        url = client.presigned_get_object(
                    bucket_name=str(owner_id),
                    object_name=file.filename,
                    expires=timedelta(minutes=1),
                    )

        documents.append({"id":str(file.file_id),
                          "name": file.filename, 
                          "createdAt":file.createdat or "1970-01-01",
                          "lastModified":file.lastmodified or "1970-01-01",
                          "url":url,
                          "type":file.type,
                          "size":file.size,
                          "ownerName":"user",
                          "sharedWith":file.shared_with,
                          "bucket":file.owner_id
                          })
    return documents

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
