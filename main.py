import bugzilla
import datetime
import time

from IssueTypes import IssueTypes
from Queries import Queries

bug_dict = {}

options = """
choose one of the following options:

default: show the next bug
      a: display all bugs
      q: quit
      r: refresh the list of bugs
"""

def main():
    proceed = True
    print("Welcome to 3age!")
    print("Creating initial bug dictionary\n")
    refresh_bugs()
    while proceed:
        print(options)
        choice = input("What do you want to do? ")
        proceed = handle_choice(choice)

def handle_choice(choice):
    if choice == "":
        print("\nShowing the next bug\n")
        next_bug, type_string = get_next_bug()
        if next_bug is None:
            print("No more bugs, time to go to the pub :-D")
            return False
        else:
            print(f'[{type_string}] - {next_bug.summary}\n{next_bug.weburl}') 
            return True
    elif choice == "a":
        print("\nShowing all bugs\n")
        show_all_bugs()
        return True
    elif choice == "q":
        print("\nThanks for playing!\n")
        return False
    elif choice == "r":
        print("\nRegenerating bug list\n")
        refresh_bugs()
        return True

def get_next_bug():
    next_bug = None
    for query in Queries:
        for issue_type in IssueTypes:
            type_string = "%s_%s" % (query.name, issue_type.value)
            if len(bug_dict[type_string]) > 0:
                next_bug = bug_dict[type_string][0]
    return next_bug, type_string
            

def show_all_bugs():
    for query in Queries:
        if len(bug_dict[query.name]) > 0:
            for bug in bug_dict[query.name]:
                print(f'{bug.summary}\n{bug.weburl}\n') 

def find_bugs(bugs, issue_type):
    if issue_type == IssueTypes.NEW.value:
        return find_new_bugs(bugs)
    if issue_type == IssueTypes.REGRESSIONS.value:
        return find_regressions(bugs)

def find_new_bugs(bugs):
    result = []
    if len(bugs) > 0:
        for bug in bugs:
            creation_time = datetime.datetime.strptime(str(bug.creation_time), '%Y%m%dT%H:%M:%S')
            if datetime.datetime.now() - creation_time < datetime.timedelta(days=14):
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
    """
    URL = "bugzilla.redhat.com"
    bzapi = bugzilla.Bugzilla(URL)
    #bzapi.interactive_login()
    for query in Queries:
        query_to_send = bzapi.url_to_query(query.value)
        query_to_send["include_fields"] = ["creator", "creation_time", "id", "summary", "weburl", "keywords", "flags"]
        all_bugs = bzapi.query(query_to_send)
        bug_dict[query.name] = all_bugs
        print("\n%s_TOTAL: %d" % (query.name, len(all_bugs)))
        for issue_type in IssueTypes:
            key_name = "%s_%s" % (query.name, issue_type.name)
            bug_dict[key_name] = find_bugs(all_bugs, issue_type.value)
            if bug_dict[key_name] is None:
                num_issues = 0
            else:
                num_issues = len(bug_dict[key_name])
            print("%s_%s: %d" % (query.name, issue_type.value, num_issues))

if __name__ == "__main__":
    main()
