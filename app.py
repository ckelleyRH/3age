# save this as app.py
from flask import Flask
import main

app = Flask(__name__)

@app.route("/")
def hello():
    return main.main()

@app.route("/github")
def github():
    return main.show_github_repos()

@app.route("/github/<repo>")
def github_issues(repo):
    return main.show_github_repo_issues(repo)

@app.route("/bugzilla")
def bugzilla():
    return main.get_bugzilla_issues()

@app.route("/bugzilla/<query>")
def bugzilla_query(query):
    return main.get_bugzilla_issues_by_query(query)
