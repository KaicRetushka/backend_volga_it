from pydantic import BaseModel
from datetime import datetime

class AddHospital(BaseModel):
    hospital_id: int
    doctor_id: int
    from_time: datetime
    to_time: datetime
    room: str

class GetTimetable(BaseModel):
    timetable_id: int
    hospital_id: int
    doctor_id: int
    from_time: datetime
    to_time: datetime
    room: str

class DatetimeAppointment(BaseModel):
    from_time: datetime
    to_time: datetime

class PostAppointment(BaseModel):
    time: datetime

class ResPostAppointment(BaseModel):
    message: str
    appointment_id: int