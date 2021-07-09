import pprint
import bugzilla

def main():
    URL = "bugzilla.redhat.com"
    bzapi = bugzilla.Bugzilla(URL)
    bug = bzapi.getbug(1843501)
    comments = bug.getcomments()
    for comment in comments:
        print(comment["creator"] + ":\n" + comment["text"] + "\n\n")

if __name__ == "__main__":
    main()
