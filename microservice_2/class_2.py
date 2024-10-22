from typing import List
from pydantic import BaseModel

class Hospital(BaseModel):
    id: int
    name: str

class DataHospital(BaseModel):
    id: int
    name: str
    addres: str
    contact_phone: str

class AddHospital(BaseModel):
    name: str
    addres: str
    contact_phone: str
    rooms: List[str]
