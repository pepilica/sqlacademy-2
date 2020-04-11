from requests import get, post, delete


print(get('http://127.0.0.1:8080/api/v2/users/1').json())  # верный запрос
print(get('http://127.0.0.1:8080/api/v2/users/999').json())  # пользователя с id == 999 не существует
print(delete('http://127.0.0.1:8080/api/v2/users/1').json())  # верный запрос
print(delete('http://127.0.0.1:8080/api/v2/users/999').json())  # пользователя с id == 999 не существует
print(get('http://127.0.0.1:8080/api/v2/users').json())  # верный запрос
print(post('http://127.0.0.1:8080/api/v2/users', json={}).json())  # пустой запрос
print(post('http://127.0.0.1:8080/api/v2/users', json={
    'name': 'name',
    'surname': 'surname',
    'user_id': 10,
    'position': 'position',
    'speciality': 'speciality',
    'address': 'address',
    'email': 'email@email.com',
    'age': 55,
}).json())  # неполный запрос
print(post('http://127.0.0.1:8080/api/v2/users', json={
    'name': 'name',
    'surname': 'surname',
    'user_id': 10,
    'position': 'position',
    'speciality': 'speciality',
    'address': 'address',
    'email': 'email@email.com',
    'age': 55,
    'password': 'password'
}).json())  # верный запрос
