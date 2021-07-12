import bugzilla
import datetime
import time

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
        next_bug = get_next_bug()
        if next_bug is None:
            print("No more bugs, time to go to the pub :-D")
            return False
        else:
            print(next_bug.id, next_bug.summary) 
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
        if len(bug_dict["%s_NEW" % query.name]) > 0:
            next_bug = bug_dict["%s_NEW" % query.name][0]
        elif len(bug_dict["%s_REGRESSIONS" % query.name]) > 0:
            next_bug = bug_dict["%s_REGRESSIONS" % query.name][0]
    return next_bug
            

def show_all_bugs():
    for query in Queries:
        if len(bug_dict[query.name]) > 0:
            for bug in bug_dict[query.name]:
                print(bug.id, bug.summary) 

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
        bug_dict["%s_NEW" % query.name] = find_new_bugs(all_bugs)
        bug_dict["%s_REGRESSIONS" % query.name] = find_regressions(all_bugs)
        print("%s_TOTAL      : %d" % (query.name, len(all_bugs)))
        print("%s_NEW        : %d" % (query.name, len(bug_dict["%s_NEW" % query.name])))
        print("%s_REGRESSIONS: %d\n" % (query.name, len(bug_dict["%s_REGRESSIONS" % query.name])))

if __name__ == "__main__":
    main()
