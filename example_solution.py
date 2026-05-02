import requests as rq
import json
from operator import itemgetter
'''
# get example
r = requests.get(url)

# post example
payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.post(url, data=payload)
'''

# general
server_url = "http://localhost:8080"
hahaton_easy_url = server_url+"/hahaton/easy/task/"
url = hahaton_easy_url

# first task
def solve_task_1(data: str):
    task: dict = json.loads(data)
    scores: list[dict] = []
    for i in task['applicants']:
        score = 0
        if i['git']: score+=10
        if i['project_experience']: score+=20
        if 20<=i['free_time']<40: score+=10
        if i['free_time']>=40: score+=20
        scores.append({'name':i['name'], 'uuid':i['uuid'], 'score':score})
    sorted_applicants = sorted(scores, key=itemgetter('score', 'uuid'))
    return json.dumps({'best':sorted_applicants})

task_url = url + '1'
r = rq.get(task_url)
print(r.text)
solution = solve_task_1(r.text)
payload = {'team':'FVS_bratva', 'solution':solution}
r = rq.post(task_url, data=payload)
print(r.text)
