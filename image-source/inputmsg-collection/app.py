import json
import os

import requests
from pyace import ACEAdminConnection, subdirs_file_content_to_dict


def jsonize(x):
    """Function to output the camelcased hyphenated input string: sheep-horse-cow -> sheepHorseCow

    :param x: input
    :type x: string
    :returns: camelcased string"""
    arr = x.split('-')
    arr[1:] = map(lambda x: x.capitalize(), arr[1:])
    return "".join(arr)


def upload_to_inputmsg_api(upload_payload):
    """Method to upload the ACE Records to the input-msg-api. Prints whether successful but does not raise errors.
    If uploading the test records was successful, the recorded data is cleaned for the ACE server

    :param upload_payload: list of ACE record (as dictionary, not as the class instance)
    :type upload_payload: list(dict)"""
    print(f"Found {len(upload_payload)} records (not all of which are input messages)...")
    print("Uploading records to inputmsg-api...")
    upload_response = requests.post(f"http://inputmsg-api-svc:8080", auth=upload_auth, data=json.dumps(upload_payload),
                                    verify=False, params=None)
    if upload_response.status_code == 201:
        print("Successful!")
        print("Deleting the test date from the ACE server...")
        ace_conn.delete_recorded_test_data()
        print("Successful!")
    else:
        print(
            f"Unsuccessful. Status code {upload_response.status_code}. Response: {upload_response.content.decode('utf-8')}")


def is_flow_recording_on(flow_uri):
    """Method to extract a boolean from the ACE server indicating whether recording is on for that particular flow.

    :param flow_uri: ACE Admin REST API Flow URI string: /apiv2/{project_type}/{project}/messageflows/{message_flow}
    :type flow_uri: string
    :returns: boolean"""
    return ace_conn.get(uri=f"{flow_uri}", expected_rc=200, parse_json=True, params=None,
                        func=lambda x: "stop-recording" in x["actions"]["available"].keys())


def get_msgflows_of_project(project_uri):
    """Method to extract a tuple of tuples, one tuple per project's message flow, with each tuple containing
     0) the message flow name
     1) the message flow URI

    Example return element:
    ("brokerSchema1.Flow1", "/apiv2/applications/Project1/messageflows/brokerSchema1.Flow1")

    :param project_uri: ACE Admin REST API Flow URI string: /apiv2/{project_type}/{project}
    :type project_uri: string
    :returns: tuple of size two tuples"""
    return ace_conn.get(uri=f"{project_uri}/messageflows", expected_rc=200, parse_json=True, params=None,
                        func=lambda x: tuple((y["name"], y["uri"]) for y in x["children"]))


def get_projects_of_type(project_type):
    """Method to extract a tuple of tuples, one per currently running project of a specific type
    (applications/services/rest-apis), with each tuple containing
    0) the project name
    1) the project URI

    Example return element:
    ("Project1", "/apiv2/rest-apis/Project1")

    :param project_type: choice string of applications/services/rest-apis
    :type project_type: string
    :returns: tuple of size two tuples"""
    return ace_conn.get(uri=f"/apiv2/{project_type}", expected_rc=200, parse_json=True, params=None,
                        func=lambda x: tuple((y["name"], y["uri"]) for y in x["children"]))


def get_running_project_types():
    """Method to extract a dictionary with the three project types as keys and a boolean as value. This boolean will be
    True if there exists a running project on th ACE server of that project type

    :returns: dictionary. Keys (string): the project types. Value (boolean): True if the ACE server currently has a
    project running of that type"""
    return ace_conn.get(uri="/apiv2", expected_rc=200, parse_json=True, params=None,
                        func=lambda x: dict((y, x["children"][jsonize(y)]["hasChildren"]) for y in project_types))


mount_path = os.environ.get('EOD20_INPUTMSGCOLL_MOUNT_PATH')
ace_config_dir = os.path.join(mount_path, "ace-config")
api_user_dir = os.path.join(mount_path, "api-user")

ace_config = subdirs_file_content_to_dict(ace_config_dir, subdict_by_path=True, split_by_line=False)
api_users = subdirs_file_content_to_dict(api_user_dir, subdict_by_path=True, split_by_line=False)
user, pw = list(api_users.items())[0]

ace_auth = requests.auth.HTTPBasicAuth(ace_config["user"], ace_config["pw"])
upload_auth = requests.auth.HTTPBasicAuth(user, pw)

ace_conn = ACEAdminConnection(host=ace_config["host"], admin_port=int(ace_config["port"]), admin_https=False,
                              user=ace_config["user"], pw=ace_config["pw"])

# get input messages from ACE server
print("Getting recorded test data from ACE server...")
input_messages = ace_conn.get_recorded_test_data()

if len(input_messages) == 0:
    print("No records available...")
else:
    upload_to_inputmsg_api(input_messages)

print()
print("Making sure recording is switched on all flows...")
# determine which project types are deployed on the ACE server
project_types = ("applications", "rest-apis", "services")
has_project_types = get_running_project_types()

# for each project type currently deployed on the ACE server..
for project_type in filter(lambda x: has_project_types[x], project_types):
    projects = get_projects_of_type(project_type)
    print(project_type)
    # for each project name..
    for project_name, project_uri in projects:
        flows = get_msgflows_of_project(project_uri)
        print("\t", project_name)
        # for each flow in the project..
        for flow_name, flow_uri in flows:
            recording_on = is_flow_recording_on(flow_uri)
            print("\t" * 2, flow_name, end=": ")
            # if recording is not on, switch it on..
            if not recording_on:
                ace_conn.post(uri=f"{flow_uri}/start-recording", data="", expected_rc=200, parse_json=False)
                print("Switched ON")
            else:
                print("Already ON")
