from pyace.ace import ACEConnection
from pyace.ace import ACERecord
import os
import json
import requests

ace_config_dir = os.path.join(os.path.abspath(os.sep), "ace-config")
api_user_dir = os.path.join(os.path.abspath(os.sep), "api-user")

ace_config = dict()
for file in ("host", "port", "https", "user", "pw"):
    f = open(os.path.join(ace_config_dir, file), "r")
    value = f.readlines()[0]
    ace_config[file] = value
    f.close()

user = list(filter(lambda x: x[:2] != "..", os.listdir(api_user_dir)))[0]
pw = open(os.path.join(api_user_dir, user), "r").readlines()[0]

ace_auth = requests.auth.HTTPBasicAuth(ace_config["user"], ace_config["pw"])
upload_auth = requests.auth.HTTPBasicAuth(user, pw)

ace_conn = ACEConnection(
    host=ace_config["host"],
    admin_port=int(ace_config["port"]),
    http_port=7800,
    https_port=7843,
    admin_https=False
)


def jsonize(x):
    arr = x.split('-')
    arr[1:] = map(lambda x: x.capitalize(), arr[1:])
    return "".join(arr)


# get input messages from ACE server
print("Getting recorded test data from ACE server...")
input_messages = ace_conn.get(uri="/apiv2/data/recorded-test-data",
                              expected_rc=200,
                              parse_json=True,
                              auth=ace_auth,
                              params=None,
                              func=lambda x: list(ACERecord(y).test_data() for y in x.get("recordedTestData", list())))

if len(input_messages) == 0:
    print("No records available...")
else:
    print(f"Found {len(input_messages)} records (not all of which are input messages)...")

    # upload the input messages to the inputmsg-api
    print("Uploading records to inputmsg-api...")
    upload_response = requests.posts(f"inputmsg-api-svc.eod20:8080/",
                                     auth=upload_auth,
                                     data=json.dumps(input_messages),
                                     verify=False,
                                     params=None)

    if upload_response.status_code == 201:
        print("Successful! Deleting the test date from the ACE server...")
        delete_response = ace_conn.delete(uri="/apiv2/data/recorded-test-data",
                                          expected_rc=200,
                                          parse_json=False,
                                          auth=ace_auth,
                                          params=None)
        if delete_response.status_code == 201:
            print("Successful!")
        else:
            print("Unsuccessful. Please delete them manually!")
            print(
                f"Status code {delete_response.status_code}. Response: {delete_response.content.decode('utf-8')}")
    else:
        print(
            f"Unsuccessful. Status code {upload_response.status_code}. Response: {upload_response.content.decode('utf-8')}")

print()
print("Making sure recording is switched on all flows...")
# determine which project types are deployed on the ACE server
project_types = ("applications", "rest-apis", "services")
has_project_types = ace_conn.get(uri="/apiv2",
                                 expected_rc=200,
                                 parse_json=True,
                                 auth=ace_auth,
                                 params=None,
                                 func=lambda x: dict(
                                     (y, x["children"][jsonize(y)]["hasChildren"]) for y in project_types))

data = dict()
# for each project type currently deployed on the ACE server
for project_type in filter(lambda x: has_project_types[x], project_types):
    projects = ace_conn.get(uri=f"/apiv2/{project_type}",
                            expected_rc=200,
                            parse_json=True,
                            auth=ace_auth,
                            params=None,
                            func=lambda x: tuple((y["name"], y["uri"]) for y in x["children"]))
    data[project_type] = dict((name, dict()) for name, uri in projects)
    print(project_type)
    # for each project name
    for project_name, project_uri in projects:
        flows = ace_conn.get(uri=f"{project_uri}/messageflows",
                             expected_rc=200,
                             parse_json=True,
                             auth=ace_auth,
                             params=None,
                             func=lambda x: tuple((y["name"], y["uri"]) for y in x["children"]))
        data[project_type][project_name] = dict((name, dict()) for name, uri in flows)
        print("\t", project_name)
        # for each flow in the project
        for flow_name, flow_uri in flows:
            recording_on = ace_conn.get(uri=f"{flow_uri}",
                                        expected_rc=200,
                                        parse_json=True,
                                        auth=ace_auth,
                                        params=None,
                                        func=lambda x: "stop-recording" in x["actions"]["available"].keys())
            print("\t" * 2, flow_name, end=": ")

            # if recording is not on
            if not recording_on:
                recording_toggle = ace_conn.post(uri=f"{flow_uri}/start-recording",
                                                 data="",
                                                 expected_rc=200,
                                                 parse_json=False,
                                                 auth=ace_auth)
                print("Switched ON")
            else:
                print("Already ON")
