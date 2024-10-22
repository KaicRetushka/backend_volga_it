from typing import List
from pydantic import BaseModel

class add_user(BaseModel):
    last_name: str
    first_name: str
    username: str
    password: str

class res_jwt_user(BaseModel):
    message: str
    refresh_token: str
    access_token: str

class username_and_password(BaseModel):
    username: str
    password: str

class req_update_jwt(BaseModel):
    refresh_token: str

class data_account(BaseModel):
    username: str
    password: str
    role: List
    last_name: str
    first_name: str

class data_account_id(BaseModel):
    id: int
    username: str
    password: str
    role: List
    last_name: str
    first_name: str

class update_account(BaseModel):
    last_name: str
    first_name: str
    password: str

class about_user(BaseModel):
    id: int
    username: str
    password: str
    role: List[str]
    last_name: str
    first_name: str

class data_doctor(BaseModel):
    id: int
    full_name: str