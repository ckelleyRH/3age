# save this as app.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, World!\n\n<h1>HELLOOOOOOOOO<h1>"

@app.route("/<name>")
def foo(name):
    return f'Hello, {name}!'