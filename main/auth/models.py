from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    active: bool | None = None

class DataBaseUser(User):
    hashed_password: str
