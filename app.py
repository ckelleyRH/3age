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

@app.route("/cves")
def cves():
    return main.show_cves()

@app.route("/cves/<keyword>")
def cves_keyword(keyword):
    return main.show_cves_by_keyword(keyword)
