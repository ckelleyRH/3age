import bugzilla
import datetime
import pprint
import time

from IssueTypes import IssueTypes
from Queries import Queries

bug_dict = {}
URL = "bugzilla.redhat.com"
bzapi = bugzilla.Bugzilla(URL)
#bzapi.interactive_login()

options = """
choose one of the following options:

default: show the next bug
      a: display all bugs
      q: quit
      r: refresh the list of bugs
"""

triage_options = """
choose at least one of the following options:

      c: add a comment (noop)
      k: add keyword(s) (noop)
      n: skip to next bug (noop)
      q: quit (noop)
      s: change issue status (noop)
"""

def main():
    proceed = True
    print("Welcome to 3age!")
    print("Creating initial bug dictionary:")
    proceed = refresh_bugs()
    while proceed:
        print(options)
        choice = input("What do you want to do? ")
        proceed = handle_choice(choice)
    print("\nNo more bugs, time to go to the pub :-D")

def handle_choice(choice):
    if choice == "":
        print("\nShowing the next bug\n")
        next_bug, type_string = get_next_bug()
        if next_bug is None:
            return False
        else:
            triage_bug(next_bug, type_string)
            return True
    if choice == "a":
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
    else:
        print("\nInvalid option, please try again\n")
        return True

def handle_triage_choice(choice):
    if choice == "c":
        print("\nAdding comment\n")
        return True
    elif choice == "k":
        print("\nAdding keyword(s)\n")
        return True
    elif choice == "n":
        print("\Skipping to next bug\n")
        return True
    elif choice == "q":
        print("\nReturning to main menu\n")
        return False
    elif choice == "s":
        print("\nChanging bug status\n")
        return True
    else:
        print("\nInvalid option, please try again\n")
        return True

def triage_bug(next_bug, type_string):
    still_triaging = True
    bug = bzapi.getbug(next_bug.id)
    bug_comments = bug.getcomments()
    print(f'[{type_string}] - {bug.summary}\n{bug.weburl}')
    print("\n  Product    = %s" % bug.product)
    print("  Component  = %s" % bug.component)
    print("  Status     = %s" % bug.status)
    print("  Resolution = %s\n" % bug.resolution)
    for comment in bug_comments:
        print(f'{comment["creator"]}\n{comment["text"]}\n')
    while still_triaging:
        print(triage_options)
        choice = input("What do you want to do? ")
        still_triaging = handle_triage_choice(choice)

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
    @return: True if there are bugs to triage else False
    """
    total_bugs = 0
    for query in Queries:
        query_to_send = bzapi.url_to_query(query.value)
        query_to_send["include_fields"] = ["creator", "creation_time", "id", "summary", "weburl", "keywords", "flags"]
        all_bugs = bzapi.query(query_to_send)
        bug_dict[query.name] = all_bugs
        total_bugs += len(all_bugs)
        print("\n%s_TOTAL: %d" % (query.name, len(all_bugs)))
        for issue_type in IssueTypes:
            key_name = "%s_%s" % (query.name, issue_type.name)
            bug_dict[key_name] = find_bugs(all_bugs, issue_type.value)
            if bug_dict[key_name] is None:
                num_issues = 0
            else:
                num_issues = len(bug_dict[key_name])
            print("%s_%s: %d" % (query.name, issue_type.value, num_issues))
    return total_bugs != 0

if __name__ == "__main__":
    main()
