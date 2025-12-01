from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(BaseModel):
    username: str
    email: str
    active: bool | None = None

class Base(DeclarativeBase):
    pass

class UserPSQL(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    username: Mapped[str]
    email: Mapped[str]
    hashed_password: Mapped[str]
    active: Mapped[bool]

class DataBaseUser(User):
    id: uuid.UUID
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None


class LoginForm(BaseModel):
    email:str
    password:str

class CreateUserForm(BaseModel):
    username:str
    email:str
    password:str
