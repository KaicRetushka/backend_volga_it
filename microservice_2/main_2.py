from fastapi import FastAPI, Header, HTTPException, Path
from class_2 import *
from typing import List
import psycopg2
import httpx
import uvicorn
import os
import time

app = FastAPI(title='Микросервис больниц')

while True:
    try:
        connection = psycopg2.connect(database='simbir_health_db', user='postgres', password='root', host='db')
        break
    except:
        time.sleep(1)

connection.autocommit = True
cursor = connection.cursor()

@app.get('/api/Hospitals', tags=['Получение списка больниц'])
def get_hospitals(access_token: str = Header(..., alias='accessToken'), from_header: int = Header(..., alias='from'), count: int = Header(...)) -> List[Hospital]: 
    request = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Authentication/Validate''', headers={'accessToken': access_token})
    if(request.status_code == 200):
        cursor.execute('SELECT id, name FROM hospitals WHERE is_deleted=false;')
        content = cursor.fetchall()
        if(len(content) < from_header):
            raise HTTPException(status_code=400, detail='Вы указали слишком большой from')
        elif(1 > from_header):
            raise HTTPException(status_code=400, detail='Вы указали слишком маленький from')
        elif(0 > count):
            raise HTTPException(status_code=400, detail='Вы указали слишком маленький count')
        elif(len(content) - from_header + 1 < count):
            raise HTTPException(status_code=400, detail='Вы указали слишком большой count')
        else:
            list_hospitals = []
            for i in range(count):
                list_hospitals.append({'id': content[from_header + i - 1][0], 'name': content[from_header + i - 1][1]})
            return list_hospitals
    raise HTTPException(status_code=401, detail=request.json()['detail'])

@app.get('/api/Hospitals/{id}', tags=['Получение информации о больнице по Id'])
def get_hospital(id: int, access_token: str = Header(..., alias='accessToken')):
    request = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Authentication/Validate''', headers={'accessToken': access_token})
    if(request.status_code == 200):
        try:
            cursor.execute(f"""SELECT id, name, addres, contact_phone FROM hospitals WHERE id={id} AND is_deleted=false;;""")
            content = cursor.fetchall()[0]
            return {'id': content[0], 'name': content[1], 'addres': content[2], 'contact_phone': content[3]}
        except:
            raise HTTPException(status_code=400, detail='Неверный id больницы')
    raise HTTPException(status_code=request.status_code, detail=request.json()['detail'])

@app.get('/api/Hospitals/{id}/Rooms', tags=['Получение списка кабинетов больницы по Id'])
def get_rooms(id: int = Path(...), access_token: str = Header(..., alias='accessToken')):
    request = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Authentication/Validate''', headers={'accessToken': access_token})
    if(request.status_code == 200):
        try:
            cursor.execute(f"""SELECT rooms FROM hospitals WHERE id={id} AND is_deleted=false;""")
            content = cursor.fetchall()[0]
            return {'rooms': content}
        except:
            raise HTTPException(status_code=400, detail='Неверный id')
    raise HTTPException(status_code=401, detail=request.json()['detail'])

@app.post('/api/Hospitals', tags=['Создание записи о новой больнице'])
def create_hospital(body: AddHospital, access_token: str = Header(..., alias='accessToken')) -> str:
    request = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    if(request.status_code == 200):
        role = request.json()['role']
        if('Admin' in role):
            if(len(body.contact_phone) > 12):
                raise HTTPException(status_code=400, detail='Номер телефона слишком длинный')
            elif(len(body.rooms) == 0):
                raise HTTPException(status_code=400, detail='Добавте хотя бы один кабинет')
            cursor.execute(f"""INSERT INTO hospitals(name, addres, contact_phone, rooms) VALUES('{body.name}', '{body.addres}', {body.contact_phone}, ARRAY{body.rooms});""")
            return 'Больница добавлена'
        raise HTTPException(status_code=401, detail='Вы не являетесь администратором')
    raise HTTPException(status_code=401, detail=request.json()['detail'])

@app.put('/api/Hospitals/{id}', tags=['Изменение информации о больнице по Id'])
def put_hospital(body: AddHospital, id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    request = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    if(request.status_code == 200):
        role = request.json()['role']
        if('Admin' in role):
            try:
                cursor.execute(f"""SELECT * FROM hospitals WHERE id={id} AND is_deleted=false;;""")
                content = cursor.fetchall()[0]
                if(len(body.contact_phone) > 12):
                    raise HTTPException(status_code=400, detail='Номер телефона слишком длинный')
                elif(len(body.rooms) == 0):
                    raise HTTPException(status_code=400, detail='Добавте хотя бы один кабинет')
                cursor.execute(f"""UPDATE hospitals SET name='{body.name}', addres='{body.addres}', contact_phone='{body.contact_phone}', rooms=ARRAY{body.rooms} WHERE id={id}""")
                return 'Больница изменена'
            except:
                raise HTTPException(status_code=400, detail='Не существует такой больницы')
        raise HTTPException(status_code=401, detail='Вы не являетесь администратором')
    raise HTTPException(status_code=401, detail=request.json()['detail'])

@app.delete('/api/Hospitals/{id}',  tags=['Мягкое удаление записи о больнице'])
def delete_hospital(id: int = Path(...), access_token: str = Header(..., alias='accessToken')):
    request = httpx.get(f'''{os.environ["APP_1_URL"]}/api/Accounts/Me''', headers={'accessToken': access_token})
    if(request.status_code == 200):
        role = request.json()['role']
        if('Admin' in role):
            try:
                cursor.execute(f"""SELECT * FROM hospitals WHERE id={id} AND is_deleted=false;;""")
                content = cursor.fetchall()[0]
                cursor.execute(f"""UPDATE hospitals SET is_deleted=true WHERE id={id}""")
                return 'Больница удалена'
            except:
                raise HTTPException(status_code=400, detail='Не существует такой больницы')
        raise HTTPException(status_code=401, detail='Вы не являетесь администратором')
    raise HTTPException(status_code=401, detail=request.json()['detail'])
    

if (__name__ == '__main__'):
    uvicorn.run('main_2:app', reload=True, host='0.0.0.0', port=8082)