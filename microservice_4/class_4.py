from pydantic import BaseModel
from datetime import datetime

class AddHistory(BaseModel):
    date: datetime
    pacient_id: int
    hospital_id: int
    doctor_id: int
    room: str
    data: str

class ResPostHistory(BaseModel):
    message: str
    history_id: int

class ShortDataHistory(BaseModel):
    history_id: int
    date: datetime

class DataHistory(BaseModel):
    history_id: int
    date: datetime  
    pacient_id: int  
    hospital_id: int
    doctor_id: int
    room: str
    data: str