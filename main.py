#!/usr/bin/python3
import os
from flask import Flask, render_template, request, url_for, flash, redirect, make_response, Response
import sqlite3
from waitress import serve
from werkzeug.utils import secure_filename
import hahaton_tasks
from hahaton_tasks import generate_tasks, verify_tasks
import base64
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
conn = sqlite3.connect('progress.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS progress (submissionId INTEGER PRIMARY KEY , team TEXT, taskId INTEGER, time DATETIME DEFAULT CURRENT_TIMESTAMP )')
cursor.close()
conn.close()

def next_task_id(taskid: int) -> str:
    return str(base64.encodebytes(bytes(str(taskid+1), encoding="ASCII")), encoding="ASCII")

def verify_easy_solution(taskid: int, solution: str) -> (bool, str):
    return verify_tasks[int(taskid)-1](solution)

@app.route("/hahaton/progress")
def teams_progress():
    conn = sqlite3.connect('progress.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress")
    progress = cursor.fetchall()
    if progress == None:
        return "Noone finished any tasks =["
    return progress

@app.route("/hahaton/easy/task/text/<taskid>")
def task_text_data(taskid: str):
    taskid = str(int(base64.decodebytes(bytes(taskid, encoding="ASCII"))))
    if taskid=="1":
        return render_template('task1.html')
    elif taskid=="2":
        return render_template('task2.html')
    else:
        return render_template('unknowntask.html')

@app.route("/hahaton/easy/task/<taskid>", methods=('GET', 'POST'))
def task_text(taskid: str):
    taskid = str(int(base64.decodebytes(bytes(taskid, encoding="ASCII"))))
    res = ""
    if request.method != 'POST':
        if taskid.isdigit() and 0 < int(taskid) <= len(generate_tasks):
            res = generate_tasks[int(taskid)-1]()
        else:
            res = "ERROR: task id must be an integer"
        return Response(res, mimetype='text/json')
    solution = request.form["solution"]
    solved, reason = verify_easy_solution(taskid, solution)
    if solved:
        team = request.form["team"]
        conn = sqlite3.connect('progress.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO progress (team, taskId) VALUES ( ? , ?)", (team, int(taskid)))
        conn.commit()
        cursor.close()
        conn.close()
        return "Congrats! Next task id: " + str(next_task_id(int(taskid)))
    else:
        return reason + " Try again! =D"

@app.route("/doc")
def hello():
    return render_template('documentation.html')

@app.route("/")
def showIndex():
    return "First task link is " + "/hahaton/easy/task/" + next_task_id(0) + ". Good Luck!"

if __name__ == "__main__":
    port=8080
    print("Starting server on port: "+str(port))
    serve(app, host="0.0.0.0", port=port)
