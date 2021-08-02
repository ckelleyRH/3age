# save this as app.py
from flask import Flask
import main

app = Flask(__name__)

@app.route("/")
def hello():
    return main.main()

@app.route("/github")
def github():
    return main.start_github()

@app.route("/bugzilla")
def bugzilla():
    return main.get_bugzilla_issues()

@app.route("/<name>")
def foo(name):
    return f'Hello, {name}!'