import bugzilla
from github import Github
import datetime
import pprint
import time

from flask import render_template
from IssueTypes import IssueTypes 
from Queries import Queries
from pygit2.callbacks import git_clone_options

github_repos = []
bug_dict = {}
sorted_bug_dict = {}
URL = "bugzilla.redhat.com"
bzapi = bugzilla.Bugzilla(URL)
#bzapi.interactive_login()
queries = set(query.name for query in Queries)
issue_types = set(issue_type.value for issue_type in IssueTypes)
g = Github("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")
jss_repo = g.get_repo("dogtagpki/jss")
pki_repo = g.get_repo("dogtagpki/pki")
tomcatjss_repo = g.get_repo("dogtagpki/tomcatjss")

options = """
choose one of the following options:

                      return: show the next bug
        <query>_<issue type>: type a query and/or issue type to return that list of bugs
<query>_<issue type>_<index>: display info for a bug from a list
                           a: display all bugs
                           b: bulk close
                           i: show list of issue types
                           q: show list of querys
                           r: refresh the list of bugs
                           x: exit
"""

triage_options = """
choose at least one of the following options:

      c: add a comment (noop)
      k: add keyword(s) (noop)
      n: skip to next bug (noop)
      q: quit (noop)
      s: change issue status (noop)
"""

close_bug_comment = """
This issue was automatically closed due to its age.
If you would like this issue to be reconsidered by the development team please re-open the issue.
"""

def main():
    num_bugzilla_issues = refresh_bugs()
    num_github_issues = 900
    return render_template(
        'home.html',
        num_github_issues=num_github_issues,
        num_bugzilla_issues=num_bugzilla_issues)

    #===========================================================================
    # proceed = True
    # print("Welcome to 3age!")
    # print("Creating initial bug dictionary:\n")
    # proceed = refresh_bugs()
    # while proceed:
    #     print(options)
    #     choice = input("What do you want to do? ")
    #     proceed = handle_choice(choice)
    # print("\nNo more bugs, time to go to the pub :-D")
    #===========================================================================

def handle_choice(choice):
    proceed = True
    if choice == "":
        print("\nShowing the next bug\n")
        next_bug, type_string = get_next_bug()
        if next_bug is None:
            proceed = False
        else:
            triage_bug(next_bug, type_string)
    elif choice == "a":
        print("\nShowing all bugs\n")
        show_all_bugs()
    elif choice == "b":
        print("\nBulk closing bugs\n")
        close_bugs()
    elif choice == "e":
        print("\nThanks for playing!\n")
        proceed = False
    elif choice == "i":
        print("\nAvailable issue types:\n")
        show_issue_types_list()
    elif choice == "q":
        print("\nAvailable queries:\n")
        show_query_list()
    elif choice == "r":
        print("\nRegenerating bug list\n")
        refresh_bugs()
    else:
        resolve_complex_choice(choice)
    return proceed

def handle_triage_choice(choice, bug):
    proceed = True
    if choice == "c":
        print("\nAdding comment\n")
    if choice == "close":
        print("\nClosing bug\n")
        close_bug(bug)
        refresh_bugs()
    elif choice == "k":
        print("\nAdding keyword(s)\n")
    elif choice == "n":
        print("\Skipping to next bug\n")
    elif choice == "q":
        print("\nReturning to main menu\n")
        proceed = False
    elif choice == "s":
        print("\nChanging bug status\n")
    else:
        print("\nInvalid option, please try again\n")
    return proceed

def resolve_complex_choice(choice):
    query, issue_type, index = parse_choice(choice)
    if query and issue_type:
        type_string = f'{query}_{issue_type}'
        if index:
            if index < len(bug_dict[f'{type_string}']):
                triage_bug(bug_dict[f'{type_string}'][index], type_string)
        else:
            show_bugs(bug_dict[f'{type_string}'])
    elif query:
        if index:
            if index < len(bug_dict[query]):
                triage_bug(bug_dict[query][index], query)
        else:
            show_bugs(bug_dict[query])
    elif issue_type:
        if index:
            if index < len(bug_dict[issue_type]):
                triage_bug(bug_dict[issue_type][index], issue_type)
        else:
            show_bugs(bug_dict[issue_type])
    else:
        print("\nInvalid option, please try again\n")

def triage_bug(next_bug, type_string):
    still_triaging = True
    bug = bzapi.getbug(next_bug.id)
    bug_comments = bug.getcomments()
    print(f'[{type_string}] - {bug.summary}\n{bug.weburl}\n')
    print(f'Creator    = {bug.creator} at {bug.creation_time}')
    print(f'Component  = {bug.component} in component {bug.product}')
    print(f'Keywords   = {bug.keywords}')
    print(f'Status     = {bug.status}')
    print(f'Flags      = {bug.flags}\n')
    for comment in bug_comments:
        print(f'****{comment["creator"]} said:****\n{comment["text"]}\n****\n')
    while still_triaging:
        print(triage_options)
        choice = input("What do you want to do? ")
        still_triaging = handle_triage_choice(choice, bug)

def parse_choice(choice):
    query = None
    issue_type = None
    index = None
    choice_list = choice.split("_", 3)[:3] # strip additional args
    print(choice_list)
    if len(choice_list) == 3:
        if choice_list[0] in queries:
            query = choice_list[0]
        if choice_list[1] in issue_types:
            issue_type = choice_list[1]
        try:
            index = int(choice_list[2])
        except ValueError:
            pass
    if len(choice_list) == 2:
        if choice_list[0] in queries:
            query = choice_list[0]
        if choice_list[0] in issue_types:
            issue_type = choice_list[0]
        if choice_list[1] in issue_types:
            issue_type = choice_list[1]
        try:
            index = int(choice_list[1])
        except ValueError:
            pass 
    if len(choice_list) == 1:
        if choice_list[0] in queries:
            query = choice_list[0]
        if choice_list[0] in issue_types:
            issue_type = choice_list[0]
    return query, issue_type, index
        
def get_next_bug():
    next_bug = None
    for query in Queries:
        for issue_type in IssueTypes:
            type_string = f'{query.name}_{issue_type.value}'
            if len(bug_dict[type_string]) > 0:
                next_bug = bug_dict[type_string][0]
    return next_bug, type_string

def close_bugs():
    resolution = "WONTFIX"
    key = input("Provide dictionary key for bugs to clear: ")
    if key not in bug_dict.keys():
        print("Invalid key")
        return
    choice = input(f'You are about to close {len(bug_dict[key])} bugs as {resolution}, are you sure? (y)')
    if choice == "y":
        for bug in bug_dict[key]:
            close_bug(bug, resolution, close_bug_comment, False)
        refresh_bugs()

def close_bug(bug, resolution="WONTFIX", comment=close_bug_comment, confirm=True):
    if confirm == True:
        choice = input(f'You are about to close this bug as {resolution}, with message:\n{comment}\nAre you sure? (y)')
        if choice != "y":
            return
    bug.close(resolution="WONTFIX", comment=comment)

def show_all_bugs():
    for query in Queries:
        print(f'{query.name}:')
        show_bugs(bug_dict[query.name])

def show_issue_types_list():
    for issue_type in IssueTypes:
        print(issue_type.name) 

def show_query_list():
    for query in Queries:
        print(query.name)

def show_bugs(bugs):
    if len(bugs) == 0:
        print("\nNo bugs to show\n")
        return
    i = 0
    for bug in bugs:
        print(f'\n[{i}] {bug.summary}\n{bug.weburl}\n')
        i += 1 

def find_bugs(bugs, issue_type):
    if issue_type == IssueTypes.NEW.value:
        return find_new_bugs(bugs)
    if issue_type == IssueTypes.REGRESSIONS.value:
        return find_regressions(bugs)
    if issue_type == IssueTypes.OLD.value:
        return find_old_bugs(bugs)

def find_new_bugs(bugs):
    result = []
    if len(bugs) > 0:
        for bug in bugs:
            creation_time = datetime.datetime.strptime(str(bug.creation_time), '%Y%m%dT%H:%M:%S')
            if datetime.datetime.now() - creation_time < datetime.timedelta(days=14):
                result.append(bug)
    return result

def find_old_bugs(bugs):
    result = []
    if len(bugs) > 0:
        for bug in bugs:
            creation_time = datetime.datetime.strptime(str(bug.creation_time), '%Y%m%dT%H:%M:%S')
            if datetime.datetime.now() - creation_time > datetime.timedelta(days=365*7):
                result.append(bug)
    return result

def find_regressions(bugs):
    result = []
    if len(bugs) > 0:
        for bug in bugs:
            if "Regression" in bug.keywords:
                result.append(bug)
    return result

def refresh_bugs():
    """
    Regenerates list of bugs to triage
    @return: True if there are bugs to triage else False
    """
    total_bugs = 0
    bug_dict.clear()
    for query in Queries:
        query_to_send = bzapi.url_to_query(query.value)
        query_to_send["include_fields"] = ["creator", "creation_time", "id", "summary", "weburl", "keywords", "flags"]
        all_bugs = bzapi.query(query_to_send)
        bug_dict[query.name] = all_bugs
        total_bugs += len(all_bugs)
        for issue_type in IssueTypes:
            key_name = f'{query.name}_{issue_type.name}'
            bug_dict[key_name] = find_bugs(all_bugs, issue_type.value)
            if issue_type.value in bug_dict.keys():
                bug_dict[issue_type.value] = bug_dict[issue_type.value] + bug_dict[key_name]
            else:
                bug_dict[issue_type.value] = bug_dict[key_name]
    for key in sorted(bug_dict.keys()):
        print(f'{key:<16}: {len(bug_dict[key]):>3}')
        sorted_bug_dict[key] = bug_dict[key]

    return total_bugs

def show_github_repos():
    return """
        <a href="http://127.0.0.1:5000/github/jss">JSS Issues</a>
        </br>
        <a href="http://127.0.0.1:5000/github/pki">PKI Issues</a>
        </br>
        <a href="http://127.0.0.1:5000/github/tomcatjss">TOMCATJSS Issues</a>
    """

def show_github_repo_issues(repo):
    if repo == "jss":
        result = "<h1>All issues from Github for JSS:<br/></h1>"
        for issue in jss_repo.get_issues():
            result += f'{issue.title}<br/><a href="{issue.html_url}">{issue.html_url}</a><br/><br/>'
    if repo == "pki":
        result = "<h1>All issues from Github for PKI:<br/></h1>"
        for issue in pki_repo.get_issues():
            result += f'{issue.title}<br/><a href="{issue.html_url}">{issue.html_url}</a><br/><br/>'
    if repo == "tomcatjss":
        result = "<h1>All issues from Github for TOMCATJSS:<br/></h1>"
        for issue in tomcatjss_repo.get_issues():
            result += f'{issue.title}<br/><a href="{issue.html_url}">{issue.html_url}</a><br/><br/>'                        
    return result

def get_bugzilla_issues():
    if not bug_dict:
        refresh_bugs()
    return render_template('report-template.html', result=sorted_bug_dict)

def get_bugzilla_issues_by_query(query):
    result = ""
    for bug in bug_dict[query]:
        result += f'<a href="{bug.weburl}">{bug.id}</a>: {bug.summary}</br></br>'
    return result
        

if __name__ == "__main__":
    main()
