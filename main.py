import bugzilla
import datetime
import time

from Queries import Queries

bug_dict = {}

options = """
choose one of the following options:

default: show the first bug
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
        print("Showing the next bug")
        for bug in bug_dict["RHCS_TO_TRIAGE_NEW"]:
            print(bug.id, bug.summary)
        return True
    elif choice == "q":
        print("Thanks for playing!")
        return False
    elif choice == "r":
        print("Regenerating bug list")
        return True
    
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
        print("%s: %d" % (query.name, len(all_bugs)))
        print("    NEW: %d" % len(bug_dict["%s_NEW" % query.name]))
 #       for newbug in bug_dict["%s_NEW" % query.name]:
 #           print("        %s" % newbug.summary)
 #           print("        %s" % newbug.weburl)
 #           print("\n")
        print("    REGRESSIONS: %d\n" % len(bug_dict["%s_REGRESSIONS" % query.name]))
 #       for regression in bug_dict["%s_REGRESSIONS" % query.name]:
 #           print("        %s" % regression.summary)
 #           print("        %s" % regression.weburl)
 #           print("\n")

if __name__ == "__main__":
    main()
