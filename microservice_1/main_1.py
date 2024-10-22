from class_1 import * 
from fastapi import FastAPI, HTTPException, Header, Path
from datetime import datetime, timedelta
from typing import List
import uvicorn
import psycopg2
import jwt
import time

app = FastAPI(title='Микросервис аккаунтов')


while True:
    try:
        connection = psycopg2.connect(database='simbir_health_db', user='postgres', password='root', host='db')
        break
    except:
        time.sleep(1)

connection.autocommit = True
cursor = connection.cursor()

def check_access(access_token):
    try:
        data_access = jwt.decode(access_token, 'access', algorithms=['HS256'])
        cursor.execute('SELECT * FROM users WHERE is_deleted=false;')
        content = cursor.fetchall()
        is_user  = False
        for user in content:     
            if(data_access['username'] == user[1] and data_access['password'] == user[2]):
                is_user = True
                if(user[6] == False):
                    return False
                break
        if(not(is_user)):
            return False
        return user
    except:
        return False

def check_admin(access_token):
    user = check_access(access_token)
    if(user == False):
        return {'status_code': 401,'message': 'Неверный токен доступа'}
    list_roles = user[3]
    is_admin = False
    for role in list_roles:
        if(role == 'Admin'):
            is_admin = True
            break
    if(not(is_admin)):
        return {'status_code': 403, 'message': 'Вы не являетесь администратором'}
    return {'status_code': 200, 'user': user}

@app.post('/api/Authentication/SignUp', tags=['Регистрация нового аккаунта'])
async def new_user(body: add_user) -> res_jwt_user:
    cursor.execute('SELECT * FROM users;')
    content = cursor.fetchall()
    is_username = False
    for user in content:
        if(user[1] == body.username):
            is_username = True
            break
    if(is_username):
        raise HTTPException(status_code=403, detail = 'Такой логин занят, попробуйте другой')
    if(len(body.username) > 100):
        raise HTTPException(status_code = 400, detail = 'Слишком длинный логин')
    elif(len(body.password) > 100):
        raise HTTPException(status_code = 400, detail = 'Слишком длинный пароль')
    elif(len((body.last_name.title()).strip()) > 100):
        raise HTTPException(status_code = 400, detail = 'Слишком длинная фамилия')
    elif(len((body.first_name.title()).strip()) > 100):
        raise HTTPException(status_code = 400, detail = 'Слишком длинное имя')
    cursor.execute(f"INSERT INTO users(username, password, role, last_name, first_name, in_account) VALUES('{body.username}', '{body.password}', ARRAY['User'], '{(body.last_name.title()).strip()}', '{(body.first_name.title()).strip()}', true)")
    refresh_token = jwt.encode({'username': body.username, 'password': body.password}, 'refresh', algorithm='HS256')
    access_token = jwt.encode({'username': body.username, 'password': body.password, 'role': ['User'], 'to_date': str(datetime.now() + timedelta(minutes = 15))[0:19]}, 'access', algorithm='HS256')
    return {'message': 'Вы успешно зарегестрировались', 'refresh_token': refresh_token, 'access_token': access_token}

@app.post('/api/Authentication/SignIn', tags=['Получение новой пары jwt пользователя'])
async def get_jwt(body: username_and_password) -> res_jwt_user:
    cursor.execute('SELECT * FROM users WHERE is_deleted=false;')
    content = cursor.fetchall()
    is_username = False
    for user in content:
        if(user[1] == body.username and user[2] == body.password):
            is_username = True
            cursor.execute(f"""UPDATE users SET in_account = true WHERE id = {user[0]}""")
            break
    if(not(is_username)):
       raise HTTPException(status_code=406, detail='Неверный логин или пароль')
    refresh_token = jwt.encode({'username': body.username, 'password': body.password}, 'refresh', algorithm='HS256')
    access_token = jwt.encode({'username': body.username, 'password': body.password, 'role': user[3], 'to_date': str(datetime.now() + timedelta(minutes = 15))[0:19]}, 'access', algorithm='HS256')
    return {'message': 'Вы успешно обновили пару токенов', 'refresh_token': refresh_token, 'access_token': access_token}

@app.put('/api/Authentication/SignOut', tags=['Выход из аккаунта'])
async def exit_account(access_token: str = Header(..., alias='accessToken')) -> str:
    try:
        data_access = jwt.decode(access_token, 'access', algorithms=['HS256'])
        cursor.execute('SELECT * FROM users  WHERE is_deleted=false;')
        content = cursor.fetchall()
        for user in content:
            if(data_access['username'] == user[1] and data_access['password'] == user[2]):
                print(user[0])
                if(user[6] == True):
                    cursor.execute(f"""UPDATE users SET in_account = false WHERE id={user[0]}""")
                    return 'Вы вышли из аккаунта'
                raise HTTPException(status_code=401, detail='Вы не входили в аккаунт')
        raise HTTPException(status_code=406, detail='Неверный JWT') 
    except:
        raise HTTPException(status_code=404, detail='Неверный JWT')
    
@app.get('/api/Authentication/Validate', tags=['Интроспекция токена'])
async def validate_access_token(access_token: str = Header(..., alias='accessToken')) -> str:
    error = 'Токен доступа недействительный'
    try:
        data_access = jwt.decode(access_token, 'access', algorithms=['HS256'])
        cursor.execute('SELECT * FROM users  WHERE is_deleted=false;')
        content = cursor.fetchall()
        is_user  = False
        for user in content:
            if(data_access['username'] == user[1] and data_access['password'] == user[2]):
                is_user = True
                if(user[6] == False):
                    raise HTTPException(status_code=406, detail='Токен доступа недействительный')
                elif(datetime.strptime(data_access['to_date'], '%Y-%m-%d %H:%M:%S') < (datetime.now())):
                    print(datetime.strptime(data_access['to_date'], '%Y-%m-%d %H:%M:%S') < (datetime.now()))
                    error = 'Действие токена доступа истекло'
                    raise HTTPException(status_code=401, detail='Действие токена доступа истекло') 
                break
        if(not(is_user)):
            raise HTTPException(status_code=406, detail='Токен доступа недействительный')
        return f'''Токен доступа ещё действителен {str(datetime.strptime(data_access['to_date'], '%Y-%m-%d %H:%M:%S') - datetime.now())[0:7]}'''
    except:
        raise HTTPException(status_code=400, detail=error)

@app.post('/api/Authentication/Refresh', tags=['Обновление пары токенов'])
async def update_jwt(body: req_update_jwt) -> res_jwt_user:
    data_refresh = jwt.decode(body.refresh_token, 'refresh', algorithms=['HS256'])
    cursor.execute('SELECT * FROM users  WHERE is_deleted=false;')
    content = cursor.fetchall()
    is_user  = False
    for user in content:
        if(data_refresh['username'] == user[1] and data_refresh['password'] == user[2]):
            is_user = True
            if(user[6] == False):
                raise HTTPException(status_code=406, detail='Токен обновления недействительный')
            break
    if(not(is_user)):
        raise HTTPException(status_code=406, detail='Токен обновления недействительный')
    refresh_token = body.refresh_token
    access_token = jwt.encode({'username': user[1], 'password': user[2], 'role': user[3], 'to_date': str(datetime.now() + timedelta(minutes = 15))[0:19]}, 'access', algorithm='HS256')
    return {'message': 'Вы успешно обновили пару токенов', 'refresh_token': refresh_token, 'access_token': access_token}

@app.get('/api/Accounts/Me', tags=['Получение данных о текущем аккаунте'])
async def get_account(access_token: str = Header(..., alias='accessToken')) -> data_account_id:
    user = check_access(access_token)
    if(not(user)):
        raise HTTPException(status_code=406, detail='Токен доступа недействительный')
    return {'id': user[0], 'username': user[1], 'password': user[2], 'role': user[3], 'first_name': user[5], 'last_name': user[4]}

@app.put('/api/Accounts/Update', tags=['Обновление своего аккаунта'])
def update_account(body: update_account, access_token: str = Header(..., alias='accessToken')) -> res_jwt_user:
    user = check_access(access_token)
    if(not(user)):
        raise HTTPException(status_code=406, detail='Токен доступа недействительный')
    elif(len(body.password) > 100):
        raise HTTPException(status_code = 400, detail = 'Слишком длинный пароль')
    elif(len((body.last_name.title()).strip()) > 100):
        raise HTTPException(status_code = 400, detail = 'Слишком длинная фамилия')
    elif(len((body.first_name.title()).strip()) > 100):
        raise HTTPException(status_code = 400, detail = 'Слишком длинное имя')
    cursor.execute(f"UPDATE users SET password='{body.password}', last_name = '{(body.last_name.title()).strip()}', first_name ='{(body.first_name.title()).strip()}' WHERE id={user[0]}")
    refresh_token = jwt.encode({'username': user[1], 'password': body.password}, 'refresh', algorithm='HS256')
    access_token = jwt.encode({'username': user[1], 'password': body.password, 'role': user[3], 'to_date': str(datetime.now() + timedelta(minutes = 15))[0:19]}, 'access', algorithm='HS256')
    return {'message': 'Вы успешно обновили ваш аккаунт', 'refresh_token': refresh_token, 'access_token': access_token}

@app.get('/api/Accounts', tags=['Получение списка всех аккаунтов'])
async def get_accounts(access_token: str = Header(..., alias='accessToken'), from_header: int = Header(..., alias='from'), count: int = Header(...)) -> List[about_user]:
    res = check_admin(access_token)
    if(res['status_code'] == 200):
        cursor.execute('SELECT * FROM users WHERE is_deleted=false;')
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
            list_users = []
            for i in range(count):
                list_users.append({'id': content[from_header + i - 1][0], 'username': content[from_header + i - 1][1], 'password': content[from_header + i - 1][2], 'role': content[from_header + i - 1][3], 'last_name': content[from_header + i - 1][4], 'first_name': content[from_header + i - 1][5]})
            return list_users
    raise HTTPException(status_code=res['status_code'], detail=res['message'])

@app.post('/api/Accounts', tags=['Создание администратором нового аккаунта'])
async def create_user(body: data_account, access_token: str = Header(..., alias='accessToken')) -> str:
    res = check_admin(access_token)
    if(res['status_code'] == 200):
        cursor.execute('SELECT * FROM users  WHERE is_deleted=false;')
        content = cursor.fetchall()
        is_username = False
        for user in content:
            if(user[1] == body.username):
                is_username = True
                break
        if(is_username):
            raise HTTPException(status_code=403, detail = 'Такой логин занят, попробуйте другой')
        if(len(body.username) > 100):
            raise HTTPException(status_code = 400, detail = 'Слишком длинный логин')
        elif(len(body.password) > 100):
            raise HTTPException(status_code = 400, detail = 'Слишком длинный пароль')
        elif(len((body.last_name.title()).strip()) > 100):
            raise HTTPException(status_code = 400, detail = 'Слишком длинная фамилия')
        elif(len((body.first_name.title()).strip()) > 100):
            raise HTTPException(status_code = 400, detail = 'Слишком длинное имя')
        elif(len(body.role) == 0):
                raise HTTPException(status_code=400, detail='Добавте хотя бы одину роль')
        cursor.execute(f"INSERT INTO users(username, password, role, last_name, first_name, in_account) VALUES('{body.username}', '{body.password}', ARRAY{body.role}, '{(body.last_name.title()).strip()}', '{(body.first_name.title()).strip()}', false)")
        return 'Вы успешно создали аккаунт'
    raise HTTPException(status_code=res['status_code'], detail=res['message'])

@app.put('/api/Accounts/{id}', tags=['Изменение администратором аккаунта по id'])
async def change_account(body: data_account, id: int  = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    res = check_admin(access_token)
    if(res['status_code'] == 200):
        cursor.execute('SELECT * FROM users WHERE is_deleted=false;')
        content = cursor.fetchall()
        is_username = False
        for user in content:
            if(user[1] == body.username):
                is_username = True
                break
        if(not(is_username)):
            raise HTTPException(status_code=400, detail='Вы указали неверный id')
        elif(user['id'] != id):
            raise HTTPException(status_code=400, detail='Такой логин уже занят')
        elif(len(body.username) > 100):
            raise HTTPException(status_code = 400, detail = 'Слишком длинный логин')
        elif(len(body.password) > 100):
            raise HTTPException(status_code = 400, detail = 'Слишком длинный пароль')
        elif(len((body.last_name.title()).strip()) > 100):
            raise HTTPException(status_code = 400, detail = 'Слишком длинная фамилия')
        elif(len((body.first_name.title()).strip()) > 100):
            raise HTTPException(status_code = 400, detail = 'Слишком длинное имя')
        elif(len(body.role) == 0):
            raise HTTPException(status_code=400, detail='Добавте хотя бы одину роль')
        cursor.execute(f"UPDATE users SET username='{body.username}', password='{body.password}', role=ARRAY{body.role}, last_name='{(body.last_name.title()).strip()}', first_name='{(body.first_name.title()).strip()}' WHERE id={id}")
        return 'Вы успешно обновили аккаунт'
    raise HTTPException(status_code=res['status_code'], detail=res['message'])

@app.delete('/api/Accounts/{id}', tags=['Мягкое удаление аккаунта по id'])
async def delete_account(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> str:
    res = check_admin(access_token)
    if(res['status_code'] == 200):
        try:
            cursor.execute(f"""SELECT * FROM users WHERE id={id} AND is_deleted=false""")
            cursor.fetchall()[0]
            cursor.execute(f"""UPDATE users SET is_deleted=true WHERE id={id}""")
            return 'Аккаунт успешно удалён'
        except:
            raise HTTPException(status_code=400, detail='Вы указали неверный id')
    raise HTTPException(status_code=res['status_code'], detail=res['message'])

@app.get('/api/Doctors', tags=['Получение списка докторов'])
async def get_all_doctors(access_token: str = Header(..., alias='accessToken'), name_filter: str = Header('', alias='nameFilter'), from_header: int = Header(..., alias='from'), count: int = Header(...)) -> List[data_doctor]:
    user = check_access(access_token)
    if(not(user)):
        raise HTTPException(status_code=406, detail='Токен доступа недействительный')
    cursor.execute(f"""SELECT id, CONCAT( last_name, ' ', first_name) AS full_name FROM users WHERE 'Doctor' = ANY(role) AND is_deleted=false AND CONCAT( last_name, ' ', first_name) LIKE '%{name_filter}%';""")
    content = cursor.fetchall()
    if(len(content) < from_header):
        raise HTTPException(status_code=400, detail='Вы указали слишком большой from')
    elif(1 > from_header):
        raise HTTPException(status_code=400, detail='Вы указали слишком маленький from')
    elif(0 > count):
        raise HTTPException(status_code=400, detail='Вы указали слишком маленький count')
    elif(len(content) - from_header + 1 < count):
        raise HTTPException(status_code=400, detail='Вы указали слишком большой count')
    list_doctors = []
    for i in range(count):
        list_doctors.append({'id': content[from_header + i - 1][0], 'full_name': content[from_header + i - 1][1]})
    return list_doctors

@app.get('/api/Doctors/{id}', tags=['Получение информации о докторе по Id'])
async def get_doctor(id: int = Path(...), access_token: str = Header(..., alias='accessToken')) -> data_doctor:
    user = check_access(access_token)
    if(not(user)):
      raise HTTPException(status_code=406, detail='Токен доступа недействительный')
    try:
        cursor.execute(f"""SELECT id, CONCAT( last_name, ' ', first_name) AS full_name FROM users WHERE 'Doctor' = ANY(role) AND is_deleted=false AND id={id};""")
        doctor = cursor.fetchall()[0]
        return {'id': doctor[0], 'full_name': doctor[1]}
    except:
        raise HTTPException(status_code=404, detail='доктора с таким id нет')

if (__name__ == '__main__'):
    uvicorn.run('main_1:app', reload=True, host='0.0.0.0', port=8081)