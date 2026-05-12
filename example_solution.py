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
def solve_task_1(data: str) -> str:
    task: dict = json.loads(data)
    scores: list[dict] = []
    for i in task['applicants']:
        score = 0
        if i['git']: score+=10
        if i['project_experience']: score+=20
        if 20<=i['free_time']<40: score+=10
        if i['free_time']>=40: score+=20
        scores.append({'uuid':i['uuid'],'name':i['name'],'score':score})
    sorted_applicants = sorted(scores, key=itemgetter('score', 'uuid'))[:task["vacancies"]]
    return json.dumps({'best':sorted_applicants})

# "hh:mm" -> minutes since 00:00, i.e. clock2minutes("09:15") => 9*60+15=555
def clock2minutes(time: str) -> int:
    h, m = time.split(":")
    return int(h)*60+int(m)

def minutes2clock(minutes: int):
    return str(minutes//60) + ":" + str(minutes%60)

def solve_task_2(data: str) -> str:

    def group_by_deadline(tasks: list[dict]) -> list[list[dict]]:
        groups: list[list[dict]] = [[]]
        tasks = sorted(tasks, key=lambda x: clock2minutes(x["deadline"]))
        deadline_i = tasks[0]["deadline"]
        groups_idx = 0
        for task in tasks:
            if task["deadline"] != deadline_i:
                groups_idx += 1
                groups.append([task])
                deadline_i = tasks[groups_idx]["deadline"]
            groups[groups_idx].append(task)
        return groups

    tasks:    list[dict] = json.loads(data)["tasks"]
    schedule: list[int]  = []
    time_now: int        = clock2minutes("09:00")
    grouped_tasks: list[list[dict]] = group_by_deadline(tasks)

    for group in grouped_tasks:
        group_deadline: int = clock2minutes(group[0]["deadline"])
        group = sorted(group,key=lambda x:x["duration"])
        for task in group:
            if time_now + task["duration"] > group_deadline:
                break
            # print(minutes2clock(time_now),"-",minutes2clock(time_now+task["duration"]), task["title"])
            time_now += task["duration"]
            schedule.append(task["id"])
    return json.dumps({'schedule':schedule})

task_url = url + 'MQ=='
r = rq.get(task_url)
solution = solve_task_1(r.text)
payload = {'team':'FVS_bratva', 'solution':solution}
r = rq.post(task_url, data=payload)
print(r.text)

task_url = url + 'Mg=='
r = rq.get(task_url)
solution = solve_task_2(r.text)
payload = {'team':'FVS_bratva', 'solution':solution}
r = rq.post(task_url, data=payload)
print(r.text)
