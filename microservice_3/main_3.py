from fastapi import FastAPI, Header, HTTPException, Path
from datetime import datetime, timedelta
from class_3 import *
from typing import List
import uvicorn
import psycopg2
import httpx
import os
import time

app = FastAPI(title='Микросервис расписания')

while True:
    try:
        connection = psycopg2.connect(database='simbir_health_db', user='postgres', password='root', host='db')
        break
    except:
        time.sleep(1)
connection.autocommit = True
cursor = connection.cursor()

@app.post('/api/Timetable', tags=['Создание новой записи в расписании'])
async def add_hospital(body:AddHospital, access_token: str = Header(..., alias='accessToken')) -> str:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        user = request_1.json()
        if('Admin' in user['role']) or ('Manager' in user['role']):
            request_2 = httpx.get(f"""{os.environ["APP_2_URL"]}/api/Hospitals/{body.hospital_id}""", headers={'accessToken': access_token})
            if(request_2.status_code == 200):
                request_3 = httpx.get(f"""{os.environ["APP_1_URL"]}/api/Doctors/{body.doctor_id}""", headers={'accessToken': access_token})
                if(request_3.status_code == 200):
                    if(body.from_time.microsecond == 0):
                        if(body.from_time.second == 0):
                            if(body.from_time.minute == 0 or body.from_time.minute == 30):
                                if(body.to_time.microsecond == 0):
                                    if(body.to_time.second == 0):
                                        if(body.from_time.minute == 0 or body.from_time.minute == 30):
                                            if((body.to_time - body.from_time) < timedelta(hours=12) and ((body.to_time - body.from_time) > timedelta(minutes=0))):
                                                request_4 = httpx.get(f"""{os.environ["APP_2_URL"]}/api/Hospitals/{body.hospital_id}/Rooms""", headers={'accessToken': access_token})
                                                if(request_4.status_code == 200):
                                                    if(body.room in request_4.json()['rooms'][0]):
                                                        cursor.execute(f"""INSERT INTO timetables(hospital_id, doctor_id, from_time, to_time, room) VALUES({body.hospital_id}, {body.doctor_id}, '{body.from_time}', '{body.to_time}', '{body.room}') RETURNING timetable_id;""")
                                                        timetable_id = cursor.fetchall()[0][0]
                                                        while body.from_time != body.to_time:
                                                            cursor.execute(f"""INSERT INTO appointments(timetable_id, from_time, to_time) VALUES({timetable_id}, '{body.from_time}', '{body.from_time + timedelta(minutes=30)}');""")
                                                            body.from_time += timedelta(minutes=30)
                                                        return 'Запись в расписание добавлена'
                                                    raise HTTPException(status_code=400, detail='Такого кабинета не существует не существует')
                                                raise HTTPException(status_code=request_4.status_code, detail=request_4.json()['detail'])
                                            raise HTTPException(status_code=400, detail='Разница между начлом записи и концом не должно превышать 12 часов и не должна быть отрицательной')
                                        raise HTTPException(status_code=400, detail='Время в конце записи должно быть кратно 30')
                                    raise HTTPException(status_code=400, detail='Секунды в конце записи должны равняться нулю')
                                raise HTTPException(status_code=400, detail='Миллисекунды в конце записи должны равняться нулю')
                            raise HTTPException(status_code=400, detail='Время в начале записи должно быть кратно 30')
                        raise HTTPException(status_code=400, detail='Секунды в начале записи должны равняться нулю')
                    raise HTTPException(status_code=400, detail='Миллисекунды в начале записи должны равняться нулю')
                raise HTTPException(status_code=request_3.status_code, detail=request_3.json()['detail'])
            raise HTTPException(status_code=request_2.status_code, detail=request_2.json()['detail'])
        raise HTTPException(status_code=401, detail='Вы не являетесь ни менеджером, ни администратором')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.put('/api/Timetable/{id}', tags=['Обновление записи расписания'])
async def put_timetable(body:AddHospital, id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        user = request_1.json()
        if('Admin' in user['role']) or ('Manager' in user['role']):
            try:
                cursor.execute(f"""SELECT * FROM timetables WHERE timetable_id={id};""")
                timetable = cursor.fetchall()[0]
            except:
                raise HTTPException(status_code=400, detail='Неверный id записи')
            if(timetable[6] == True):
                raise HTTPException(status_code=400, detail='Невозможно изменить запись расписания на неё уже записались')
            request_2 = httpx.get(f"""{os.environ["APP_2_URL"]}/api/Hospitals/{body.hospital_id}""", headers={'accessToken': access_token})
            if(request_2.status_code == 200):
                request_3 = httpx.get(f"""{os.environ["APP_1_URL"]}/api/Doctors/{body.doctor_id}""", headers={'accessToken': access_token})
                if(request_3.status_code == 200):
                    if(body.from_time.microsecond == 0):
                        if(body.from_time.second == 0):
                            if(body.from_time.minute == 0 or body.from_time.minute == 30):
                                if(body.to_time.microsecond == 0):
                                    if(body.to_time.second == 0):
                                        if(body.from_time.minute == 0 or body.from_time.minute == 30):
                                            if((body.to_time - body.from_time) < timedelta(hours=12) and ((body.to_time - body.from_time) > timedelta(minutes=0))):
                                                request_4 = httpx.get(f"""{os.environ["APP_2_URL"]}/api/Hospitals/{body.hospital_id}/Rooms""", headers={'accessToken': access_token})
                                                if(request_4.status_code == 200):
                                                    if(body.room in request_4.json()['rooms'][0]):
                                                        cursor.execute(f"""UPDATE timetables SET hospital_id={body.hospital_id}, doctor_id={body.doctor_id}, from_time='{body.from_time}', to_time='{body.to_time}', room='{body.room}' WHERE timetable_id={id} RETURNING timetable_id;""")
                                                        timetable_id = cursor.fetchall()[0][0]
                                                        cursor.execute(f"""DELETE FROM appointments WHERE timetable_id={timetable_id}""")
                                                        while body.from_time != body.to_time:
                                                            cursor.execute(f"""INSERT INTO appointments(timetable_id, from_time, to_time) VALUES({timetable_id}, '{body.from_time}', '{body.from_time + timedelta(minutes=30)}');""")
                                                            body.from_time += timedelta(minutes=30)
                                                        return 'Запись в расписании изменена'
                                                    raise HTTPException(status_code=400, detail='Такого кабинета не существует не существует')
                                                raise HTTPException(status_code=request_4.status_code, detail=request_4.json()['detail'])
                                            raise HTTPException(status_code=400, detail='Разница между начлом записи и концом не должно превышать 12 часов и не должна быть отрицательной')
                                        raise HTTPException(status_code=400, detail='Время в конце записи должно быть кратно 30')
                                    raise HTTPException(status_code=400, detail='Секунды в конце записи должны равняться нулю')
                                raise HTTPException(status_code=400, detail='Миллисекунды в конце записи должны равняться нулю')
                            raise HTTPException(status_code=400, detail='Время в начале записи должно быть кратно 30')
                        raise HTTPException(status_code=400, detail='Секунды в начале записи должны равняться нулю')
                    raise HTTPException(status_code=400, detail='Миллисекунды в начале записи должны равняться нулю')
                raise HTTPException(status_code=request_3.status_code, detail=request_3.json()['detail'])
            raise HTTPException(status_code=request_2.status_code, detail=request_2.json()['detail'])
        raise HTTPException(status_code=401, detail='Вы не являетесь ни менеджером, ни администратором')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.delete('/api/Timetable/{id}', tags=['Удаление записи расписания'])
async def delete_timetable(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        user = request_1.json()
        if('Admin' in user['role']) or ('Manager' in user['role']):
            try:
                cursor.execute(f"""SELECT * FROM timetables WHERE timetable_id={id};""")
                timetable = cursor.fetchall()[0]
                cursor.execute(f"""DELETE FROM timetables WHERE timetable_id={id};""")
                return 'Вы удалили запись в расписании'
            except:
                raise HTTPException(status_code=400, detail='Неверный id записи в расписании')
        raise HTTPException(status_code=401, detail='Вы не являетесь ни менеджером, ни администратором')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.delete('/api/Timetable/Doctor/{id}', tags=['Удаление записей расписания доктора'])
async def delete_doctor_timetables(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        user = request_1.json()
        if('Admin' in user['role']) or ('Manager' in user['role']):
            cursor.execute(f"""DELETE FROM timetables timetables WHERE doctor_id={id}""")
            return f'''Все записи в расписании удалены где у доктора id равно {id}'''
        raise HTTPException(status_code=401, detail='Вы не являетесь ни менеджером, ни администратором')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.delete('/api/Timetable/Hospital/{id}', tags=['Удаление записей расписания больницы'])
async def delete_hospital_timetable(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        user = request_1.json()
        if('Admin' in user['role']) or ('Manager' in user['role']):
            cursor.execute(f"""DELETE FROM timetables timetables WHERE hospital_id={id}""")
            return f'''Все записи в расписании удалены где у больницы id равно {id}'''
        raise HTTPException(status_code=401, detail='Вы не являетесь ни менеджером, ни администратором')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.get('/api/Timetable/Hospital/{id}', tags=['Получение расписания больницы по Id'])
async def get_timetable_hospital(id: int = Path(...), access_token: str = Header(..., alias='accessToken'), from_time: datetime = Header(None, alias='from'), to_time: datetime = Header(None, alias='to')) -> List[GetTimetable]:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Authentication/Validate''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        list_timetable = []
        if(from_time == None and to_time == None):
            cursor.execute(f"""SELECT * FROM timetables WHERE hospital_id={id};""")
            content = cursor.fetchall()
            for tup_time in content:
                list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        elif(from_time != None and to_time == None):
            cursor.execute(f"""SELECT * FROM timetables WHERE to_time > '{from_time}' AND hospital_id={id};""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[3] < from_time):
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': tup_time[4], 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        elif(from_time == None and to_time != None):
            cursor.execute(f"""SELECT * FROM timetables WHERE from_time < '{to_time}' AND hospital_id={id};""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[4] > to_time):
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': to_time, 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        else:
            cursor.execute(f"""SELECT * FROM timetables WHERE from_time < '{to_time}' AND to_time > '{from_time}' AND hospital_id={id};""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[3] < from_time and tup_time[4] > to_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': to_time, 'room': tup_time[5]})
                elif(tup_time[3] < from_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': tup_time[4], 'room': tup_time[5]})
                elif(tup_time[4] > to_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': to_time, 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        return list_timetable
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.get('/api/Timetable/Doctor/{id}', tags=['Получение расписания врача по Id'])
async def get_timetable_doctor(id: int = Path(...), access_token: str = Header(..., alias='accessToken'), from_time: datetime = Header(None, alias='from'), to_time: datetime = Header(None, alias='to')) -> List[GetTimetable]:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Authentication/Validate''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        list_timetable = []
        if(from_time == None and to_time == None):
            cursor.execute(f"""SELECT * FROM timetables WHERE doctor_id={id};""")
            content = cursor.fetchall()
            for tup_time in content:
                list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        elif(from_time != None and to_time == None):
            cursor.execute(f"""SELECT * FROM timetables WHERE to_time > '{from_time}' AND doctor_id={id};""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[3] < from_time):
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': tup_time[4], 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        elif(from_time == None and to_time != None):
            cursor.execute(f"""SELECT * FROM timetables WHERE from_time < '{to_time}' AND doctor_id={id};""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[4] > to_time):
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': to_time, 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        else:
            cursor.execute(f"""SELECT * FROM timetables WHERE from_time < '{to_time}' AND to_time > '{from_time}' AND doctor_id={id};""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[3] < from_time and tup_time[4] > to_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': to_time, 'room': tup_time[5]})
                elif(tup_time[3] < from_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': tup_time[4], 'room': tup_time[5]})
                elif(tup_time[4] > to_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': to_time, 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        return list_timetable
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.get('/api/Timetable/Hospital/{id}/Room/{room}', tags=['Получение расписания кабинета больницы'])
async def get_timetable_hospital(id: int = Path(...), room: str = Path(...), access_token: str = Header(..., alias='accessToken'), from_time: datetime = Header(None, alias='from'), to_time: datetime = Header(None, alias='to')) -> List[GetTimetable]:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Authentication/Validate''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        list_timetable = []
        if(from_time == None and to_time == None):
            cursor.execute(f"""SELECT * FROM timetables WHERE hospital_id={id}  AND room='{room}';""")
            content = cursor.fetchall()
            for tup_time in content:
                list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        elif(from_time != None and to_time == None):
            cursor.execute(f"""SELECT * FROM timetables WHERE to_time > '{from_time}' AND hospital_id={id}  AND room='{room}';""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[3] < from_time):
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': tup_time[4], 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        elif(from_time == None and to_time != None):
            cursor.execute(f"""SELECT * FROM timetables WHERE from_time < '{to_time}' AND hospital_id={id}  AND room='{room}';""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[4] > to_time):
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': to_time, 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        else:
            cursor.execute(f"""SELECT * FROM timetables WHERE from_time < '{to_time}' AND to_time > '{from_time}' AND hospital_id={id} AND room='{room}';""")
            content = cursor.fetchall()
            for tup_time in content:
                if(tup_time[3] < from_time and tup_time[4] > to_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': to_time, 'room': tup_time[5]})
                elif(tup_time[3] < from_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': from_time, 'to_time': tup_time[4], 'room': tup_time[5]})
                elif(tup_time[4] > to_time):
                        list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': to_time, 'room': tup_time[5]})
                else:
                    list_timetable.append({'timetable_id': tup_time[0], 'hospital_id': tup_time[1], 'doctor_id': tup_time[2], 'from_time': tup_time[3], 'to_time': tup_time[4], 'room': tup_time[5]})
        return list_timetable
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.get('/api/Timetable/{id}/Appointments', tags=['Получение свободных талонов на приём'])
def get_appointments(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> List[DatetimeAppointment]:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Authentication/Validate''', headers={'accessToken': access_token})
    if(request_1.status_code == 200):
        list_appointments = []
        cursor.execute(f"""SELECT from_time, to_time FROM appointments WHERE timetable_id={id} AND is_recorded=false;""")
        content = cursor.fetchall()
        for i in range(len(content)):
            list_appointments.append({'from_time': content[i][0], 'to_time': content[i][1]})
        return list_appointments
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.post('/api/Timetable/{id}/Appointments')
def post_appointments(body: PostAppointment ,id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> ResPostAppointment:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Authentication/Validate''', headers={'accessToken': access_token})
    request_2 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    username = request_2.json()['username']
    if(request_1.status_code == 200):
        cursor.execute(f"""SELECT * FROM appointments WHERE timetable_id={id} AND from_time='{body.time}' AND is_recorded=false;""")
        try:
            content = cursor.fetchall()[0]    
            cursor.execute(f"""UPDATE appointments SET is_recorded=true, recorded_user='{username}' WHERE timetable_id={id} AND from_time='{body.time}' RETURNING appointment_id;""")
            appointment_id = cursor.fetchall()
            cursor.execute(f"""UPDATE timetables SET is_recorded=true WHERE timetable_id={id};""")
            return {'message': 'Вы успешно записались', 'appointment_id': appointment_id[0][0]}
        except:
            raise HTTPException(status_code=400, detail='Неврный талон')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.delete('/api/Appointment/{id}', tags=['Отменить запись на приём'])
def delete_appointment(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    cursor.execute(f"""SELECT recorded_user FROM appointments WHERE appointment_id={id} AND is_recorded=true;""")
    try:
        recorded_user = cursor.fetchall()[0][0]
    except:
        raise HTTPException(status_code=400, detail='Неврный id записи на приём')
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    data_1 = request_1.json()
    if(request_1.status_code == 200):
        if(data_1['username'] == recorded_user):
            cursor.execute(f"""UPDATE appointments SET is_recorded=false WHERE appointment_id={id} RETURNING timetable_id;""")
            timetable_id = cursor.fetchall()[0][0]
            try:
                cursor.execute(f"""SELECT recorded_user FROM appointments WHERE appointment_id={id} AND is_recorded=true;""")
                cursor.fetchall[0]
            except:
                cursor.execute(f"""UPDATE timetables SET is_recorded=false WHERE timetable_id={timetable_id}""")            
            return 'Вы отменили запись'
        elif('Admin' in data_1['role']  or 'Manager' in data_1['role']):
            cursor.execute(f"""UPDATE appointments SET is_recorded=false WHERE appointment_id={id} RETURNING timetable_id;""")
            timetable_id = cursor.fetchall()[0][0]
            try:
                cursor.execute(f"""SELECT recorded_user FROM appointments WHERE appointment_id={id} AND is_recorded=true;""")
                cursor.fetchall[0]
            except:
                cursor.execute(f"""UPDATE timetables SET is_recorded=false WHERE timetable_id={timetable_id}""")  
            return 'Вы отменили запись'
        raise HTTPException(status_code=401, detail='Вы не можете отменить эту запись')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

if(__name__ == '__main__'):
    uvicorn.run('main_3:app', reload=True, host='0.0.0.0', port=8083)