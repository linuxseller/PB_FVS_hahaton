import json
import random as rnd
import uuid
from operator import attrgetter

# task 1
'''
[
  {
    "name":<str>,
    "uuid":<str>,
    "git":<bool>,
    "project_experience":<bool>,
    "free_time":<int>
  },
  ...
]
наличие Git <=> 10 points
опыт в проектах <=> 20 points
сколько часов в неделю готов работать X <=>
    | X < 20      = 0
    | 20 <= X < 40 = 10 points
    | x >= 40     = 20 points
'''
task_1_top_n = 10
def generate_task_1() -> json:
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

def solve_task_1() -> json.json:
    task: dict = generate_task_1().loads()
    scores: list[dict] = []
    for i in task['applicants']:
        score = 0
        if i['git']: score+=10
        if i['project_experience']: score+=20
        if 20<=i['free_time']<40: score+=10
        if i['free_time']>=40: score+=20
        scores.append({'name':i[name], 'uuid':i['uuid'], 'score':score})
    sorted_applicants = sorted(scores, key=attrgetter('score', 'uuid'))
    return json.dumps({'best':sorted_applicants})

def verify_task_1(solution: str) -> bool:
    try: # if json passed is invalid, jic
        json_solution = json.loads(solution)['best']
        if task_1_top_n != len(json_solution):
            return False
    except:
        return False
    actual_solution = json.loads(solve_task_1())['best']
    count = 0 # amount of solution applicants contained in actual solution
    for i in solution:
        if i not in actual_solution:
            return False
    return True

def generate_task_2():
    pass
def solve_task_2():
    pass
def verify_task_2():
    pass


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
