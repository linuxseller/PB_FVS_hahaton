import json
import random as rnd
import uuid
from operator import itemgetter

# task 1
'''
task:
{
    "vacancies": <int>,
    "applicants": [
          {
            "name":<str>,
            "uuid":<str>,
            "git":<bool>,
            "project_experience":<bool>,
            "free_time":<int>
          },
          ...
      ]
}
наличие Git <=> 10 points
опыт в проектах <=> 20 points
сколько часов в неделю готов работать X <=>
    | X < 20      = 0
    | 20 <= X < 40 = 10 points
    | x >= 40     = 20 points

response:
{
    "best": [
        {
            "name": <str>,
            "uuid": <str>,
            "score": <int>
        }
        ...
    ]
}
'''
task_1_top_n = 10
def generate_task_1() -> str:
    rnd.seed(1)
    first_names: list[str] = [
        "James", "Olivia", "Liam", "Emma", "Noah",
        "Ava", "Ethan", "Sophia", "Lucas", "Mia"
    ]

    last_names: list[str] = [
        "Smith", "Johnson", "Brown", "Williams", "Jones",
        "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"
    ]
    res: list[dict] = []
    for i in range(100):
        name: str = rnd.choice(first_names) + ' ' + rnd.choice(last_names)
        git: bool = bool(rnd.randint(0,1))
        project_experience: bool = bool(rnd.randint(0,1))
        free_time: int = rnd.randint(10,45)
        res.append({
            'name':name,
            'git':git,
            'project_experience':project_experience,
            'free_time':free_time,
            'uuid':i
            })
    task_condition: dict = {'vacancies':task_1_top_n, 'applicants':res}
    return json.dumps(task_condition)

def solve_task_1() -> str:
    task: dict = json.loads(generate_task_1())
    scores: list[dict] = []
    for i in task['applicants']:
        score = 0
        if i['git']: score+=10
        if i['project_experience']: score+=20
        if 20<=i['free_time']<40: score+=10
        if i['free_time']>=40: score+=20
        scores.append({'name':i["name"], 'uuid':i['uuid'], 'score':score})
    sorted_applicants = sorted(scores, key=itemgetter('score', 'uuid'))
    return json.dumps({'best':sorted_applicants})

def verify_task_1(solution: str) -> bool:
    try: # if json passed is invalid, jic
        json_solution = json.loads(solution)['best']
        print(task_1_top_n, len(json_solution))
        if task_1_top_n != len(json_solution):
            return False, "Some applicants should've come through"
    except:
        return False, "Incorrect json!"
    actual_solution = json.loads(solve_task_1())['best']
    count = 0 # amount of solution applicants contained in actual solution
    for i in json_solution:
        if i not in actual_solution:
            print(i)
            return False, "Wrong answer!"
    return True, None

# task 2

'''
WARNING: priority temporary is not considered and removed
task:
{
    "tasks": [
          {
            "title": <str>,
            "id": <int>,
            "duration": <int>,
            "deadline": <str: f"hh:mm">,
            "priority": <int>
          },
          ...
    ]
}
priority = range[1,20]
priority 20 => very important
priority 1 => not important

Assume working day starts at 9:00 and ends at 19:00 without lunch break.

response:
{
    "schedule": [<int>, ...]
}
'''

def generate_task_2() -> str:
    rnd.seed(1)
    task_objective: list[str] = ["fix", "write", "review", "update", "meeting with devteam on"]
    task_prjct: list[str] = ["main service", "program core", "new patch", "library module"]
    minutes = ["00", "15", "30", "45"]
    res: list[dict] = []
    for i in range(25):
        title: str = rnd.choice(task_objective) + ' ' + rnd.choice(task_prjct)
        # generate random task duration such that possible times will be sums of two "minutes"
        duration: int = sum(map(int, rnd.choices(minutes, k=2)))
        deadline: str = str(rnd.randint(10, 19)) + ":" + rnd.choice(minutes)
        # priority: int = rnd.randint(1,20)
        res.append({
            'title':title,
            'id':i,
            'duration':duration,
            'deadline':deadline
            # 'priority':priority
            })
    task_condition: dict = {'tasks':res}
    return json.dumps(task_condition)

## solve_task_2 is not needed due to several possible solutions
def solve_task_2(): # unneded
    pass
def verify_task_2(solution: str) -> (bool, str):
    def clock2minutes(time: str) -> int:
        h, m = time.split(":")
        return int(h)*60+int(m)

    try: # if json passed is invalid, jic
        json_solution = json.loads(solution)['schedule']
    except:
        return False, "Incorrect json!"
    task_cond = json.loads(generate_task_2())['tasks']
    time_now = clock2minutes("09:00")
    for i in json_solution:
        curtask = task_cond[i]
        if time_now + curtask["duration"] > clock2minutes(curtask["deadline"]):
            return False, "Oh no, some deadline is missed!"
        if time_now + curtask["duration"] > clock2minutes("19:00"):
            return False, "Working day ended, you are late!"
        time_now += curtask["duration"]
    time_left = clock2minutes("19:00") - time_now
    print(time_left)
    for i in task_cond:
        if time_left >= i["duration"] and i["id"] not in json_solution:
            return False, "Could've done more tasks!"
    return True, None


def generate_task_3():
    pass
def solve_task_3():
    pass
def verify_task_3():
    pass


def generate_task_4():
    pass
def solve_task_4():
    pass
def verify_task_4():
    pass

generate_tasks = [generate_task_1, generate_task_2, generate_task_3, generate_task_4]
verify_tasks = [verify_task_1, verify_task_2, verify_task_3, verify_task_4]
