import bugzilla
from Queries import Queries

def main():
    URL = "bugzilla.redhat.com"
    bzapi = bugzilla.Bugzilla(URL)
  #  bzapi.interactive_login()
    for query in Queries:
        query_to_send = bzapi.url_to_query(query.value)
        query_to_send["include_fields"] = ["creator", "id", "summary", "flags"]
        bugs = bzapi.query(query_to_send)
        print(query.name + ": " + str(len(bugs)))
        if len(bugs) > 0:
            blockers = 0
            for bug in bugs:
                if "release" in bug.flags:
                    blockers += 1
            print("blockers: " + str(blockers))



if __name__ == "__main__":
    main()
