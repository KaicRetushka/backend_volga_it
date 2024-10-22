from fastapi import FastAPI, Header, HTTPException, Path
from typing import List
from class_4 import *
import httpx
import psycopg2
import uvicorn
import os
import time

app = FastAPI(title='Микросервис документов')

while True:
    try:
        connection = psycopg2.connect(database='simbir_health_db', user='postgres', password='root', host='db')
        break
    except:
        time.sleep(1)
cursor = connection.cursor()
connection.autocommit = True

@app.get('/api/History/Account/{id}', tags=['Получение истории посещений и назначений аккаунта'])
def get_history_account(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> List[ShortDataHistory]:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    data_1 = request_1.json()
    if(request_1.status_code == 200):    
        if('Admin' in data_1['role'] or 'Manager' in data_1['role'] or 'Doctor' in data_1['role'] or data_1['pacient_id'] == id):
            cursor.execute(f"""SELECT * FROM history WHERE pacient_id={id}""")
            content = cursor.fetchall()
            list_history = []
            for i in range(len(content)):
                list_history.append({'history_id': content[i][0], 'date': content[i][1]})
            return list_history
        raise HTTPException(status_code=401, detail='Вы не можете получить историю посещения этого пользователя')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])  

@app.get('/api/History/{id}', tags=['Получение подробной информации о посещении и назначениях'])
def get_history(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> DataHistory:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    data_1 = request_1.json()
    if(request_1.status_code == 200):
        cursor.execute(f"""SELECT * FROM history WHERE history_id={id}""")
        content = cursor.fetchall()[0]    
        if('Admin' in data_1['role'] or 'Manager' in data_1['role'] or 'Doctor' in data_1['role'] or data_1['pacient_id'] == content[2]):
            return {'history_id': content[0], 'date': content[1], 'pacient_id': content[2], 'hospital_id': content[3], 'doctor_id': content[4], 'room': content[5], 'data': content[6]}
        raise HTTPException(status_code=401, detail='Вы не можете получить подробную информацию о посещении и назначениях посещения этого пользователя')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])  

@app.post('/api/History', tags=['Создание истории посещения и назначения'])
def post_history(body: AddHistory, access_token: str = Header(..., alias='accessToken')) -> ResPostHistory:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    data_1 = request_1.json()
    if(request_1.status_code == 200):
        if('Admin' in data_1['role'] or 'Manager' in data_1['role'] or 'Doctor' in data_1['role'] or data_1['pacient_id'] == body.pacient_id):
            if(len(body.room) > 100):
                raise HTTPException(status_code=400, detail='Слишком длинное название кабинета')
            cursor.execute(f"""INSERT INTO history(date, pacient_id, hospital_id, doctor_id, room, data) VALUES('{body.date}', {body.pacient_id}, {body.hospital_id}, '{body.doctor_id}', '{body.room}', '{body.data}') RETURNING history_id;""")
            history_id = cursor.fetchall()[0][0]
            return {'message': 'Вы создали историю посещения', 'history_id': history_id}
        raise HTTPException(status_code=401, detail='Вы не можете создавать историю посещение для пациента с таким id')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

@app.put('/api/History/{id}', tags=['Обновление истории посещения и назначения'])
def put_history(body: AddHistory, id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    request_1 = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    data_1 = request_1.json()
    if(request_1.status_code == 200):
        if('Admin' in data_1['role'] or 'Manager' in data_1['role'] or 'Doctor' in data_1['role'] or data_1['pacient_id'] == body.pacient_id):
            if(len(body.room) > 100):
                raise HTTPException(status_code=400, detail='Слишком длинное название кабинета')
            try:
                cursor.execute(f"""SELECT * FROM history WHERE history_id={id};""")
                content = cursor.fetchall()[0][0]
            except:
                raise HTTPException(status_code=400, detail='Неверный id истории посещения')
            cursor.execute(f"""UPDATE history SET date='{body.date}', pacient_id={body.pacient_id}, hospital_id={body.hospital_id}, doctor_id='{body.doctor_id}', room='{body.room}', data='{body.data}' WHERE history_id={id};""")
            return 'Вы изменили историю посещения'
        raise HTTPException(status_code=401, detail='Вы не можете изменить историю посещение для пациента с таким id')
    raise HTTPException(status_code=request_1.status_code, detail=request_1.json()['detail'])

if(__name__ == '__main__'):
    uvicorn.run('main_4:app', reload=True, host='0.0.0.0', port=8084)