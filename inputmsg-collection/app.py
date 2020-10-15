from pyace.aceconnection import ACEConnection
import os
import json
import requests

# ace_config = {
#     "host": "eod20-618dd4f5cf576582d05dea2fdbda72d6-0002.eu-de.containers.appdomain.cloud",
#     "port": 7600,
#     "https": "false",
#     "user": "admin1",
#     "pw": "admin1"
# }

os.chdir(os.path.join(os.path.abspath(os.sep), "config"))
cwd = os.getcwd()

ace_config = dict()
for file in filter(lambda x: os.path.isfile(x), os.listdir(cwd)):
    f = open(file)
    value = f.readlines()[0]
    ace_config[file] = value
    f.close()

auth = requests.auth.HTTPBasicAuth(ace_config["user"], ace_config["pw"])
ace_conn = ACEConnection(
    host=ace_config["host"],
    admin_port=ace_config["port"],
    http_port=7800,
    https_port=7843,
    admin_https=False
)


def jsonize(x):
    arr = x.split('-')
    arr[1:] = map(lambda x: x.capitalize(), arr[1:])
    return "".join(arr)


project_types = ("applications", "rest-apis", "services")
data = dict()

# determine which project types are deployed on the ACE server
has_project_types = ace_conn.get(uri="/apiv2",
                                 expected_rc=200,
                                 parse_json=True,
                                 auth=auth,
                                 params=None,
                                 func=lambda x: dict(
                                     (y, x["children"][jsonize(y)]["hasChildren"]) for y in project_types))

# for each project type currently deployed on the ACE server
for project_type in filter(lambda x: has_project_types[x], project_types):
    projects = ace_conn.get(uri=f"/apiv2/{project_type}",
                            expected_rc=200,
                            parse_json=True,
                            auth=auth,
                            params=None,
                            func=lambda x: tuple((y["name"], y["uri"]) for y in x["children"]))
    data[project_type] = dict((name, dict()) for name, uri in projects)
    print(project_type)
    # for each project name
    for project_name, project_uri in projects:
        flows = ace_conn.get(uri=f"{project_uri}/messageflows",
                             expected_rc=200,
                             parse_json=True,
                             auth=auth,
                             params=None,
                             func=lambda x: tuple((y["name"], y["uri"]) for y in x["children"]))
        data[project_type][project_name] = dict((name, dict()) for name, uri in flows)
        print("\t", project_name)
        # for each flow in the project
        for flow_name, flow_uri in flows:
            recording_on = ace_conn.get(uri=f"{flow_uri}",
                                        expected_rc=200,
                                        parse_json=True,
                                        auth=auth,
                                        params=None,
                                        func=lambda x: "stop-recording" in x["actions"]["available"].keys())
            print("\t" * 2, flow_name, end=": ")

            # if recording is not on
            if not recording_on:
                recording_toggle = ace_conn.post(uri=f"{flow_uri}/start-recording",
                                                 data="",
                                                 expected_rc=200,
                                                 parse_json=False,
                                                 auth=auth)
                print("Switched ON")
            else:
                print("Already ON")
