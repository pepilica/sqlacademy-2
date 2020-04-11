from requests import get, post, delete


print(get('http://127.0.0.1:8080/api/v2/jobs/1').json())  # верный запрос
print(get('http://127.0.0.1:8080/api/v2/jobs/999').json())  # работы с id == 999 не существует
print(delete('http://127.0.0.1:8080/api/v2/jobs/1').json())  # верный запрос
print(delete('http://127.0.0.1:8080/api/v2/jobs/999').json())  # пользователя с id == 999 не существует
print(get('http://127.0.0.1:8080/api/v2/jobs').json())  # верный запрос
print(post('http://127.0.0.1:8080/api/v2/jobs', json={}).json())  # пустой запрос
print(post('http://127.0.0.1:8080/api/v2/jobs', json={
    'team_leader': 1,
    'job': 'name',
    'work_size': 10,
    'is_finished': False,
    'hazard_level': 5,
}).json())  # неполный запрос
print(post('http://127.0.0.1:8080/api/v2/jobs', json={
    'team_leader': 1,
    'job': 'name',
    'work_size': 10,
    'is_finished': False,
    'hazard_level': '5',
}).json())  # неправильный запрос
print(post('http://127.0.0.1:8080/api/v2/jobs', json={
    'team_leader': 1,
    'job': 'name',
    'work_size': 10,
    'collaborators': '2, 3, 4',
    'is_finished': False,
    'hazard_level': 5,
}).json())  # верный запрос
