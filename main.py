#!/usr/bin/python3
import os
from flask import Flask, render_template, request, url_for, flash, redirect, make_response
import sqlite3
from waitress import serve
from werkzeug.utils import secure_filename
import hahaton_tasks
from hahaton_tasks import generate_tasks, verify_tasks

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

teams_progress_dict = {"empty":[]}
def next_task_id(taskid: int):
    return taskid+1

def verify_easy_solution(taskid: int, solution: str):
    return verify_tasks[int(taskid)-1]

@app.route("/hahaton/progress")
def teams_progress():
    return teams_progress_dict.__str__()

@app.route("/hahaton/easy/task/<taskid>", methods=('GET', 'POST'))
def task_text(taskid: str):
    res = ""
    if request.method != 'POST':
        if taskid.isdigit() and 0 < int(taskid) <= len(generate_tasks):
            res = generate_tasks[int(taskid)-1]()
        else:
            res = "ERROR: task id must be an integer"
        return res
    solution = request.form["solution"]
    if verify_easy_solution(taskid, solution):
        team = request.form["team"]
        if team not in teams_progress_dict.keys():
            teams_progress_dict[team]=[]
        if taskid not in teams_progress_dict[team]:
            teams_progress_dict[team] += [taskid]
        return "Congrats! Next task id: " + str(next_task_id(int(taskid)))
    else:
        return "Wrong answer =[, try again! :D"

@app.route("/")
def showIndex():
    return "Hello! First task link is " + "/hahaton/easy/1" + ". Good Luck!"
if __name__ == "__main__":
    port=8080
    print("Starting server on port: "+str(port))
    serve(app, host="0.0.0.0", port=port)
