from pydantic import BaseModel


class TaskBase(BaseModel):
    name: str
    task: str

class TaskCreate(TaskBase):
    pass

class TaskInDB(TaskBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    password_hash: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None