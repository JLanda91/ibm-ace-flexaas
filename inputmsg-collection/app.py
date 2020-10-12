import os
import json
import requests

ace_config = {
    "host": "eod20-618dd4f5cf576582d05dea2fdbda72d6-0002.eu-de.containers.appdomain.cloud",
    "port": 7600,
    "https": "false",
    "user": "admin1",
    "pw": "admin1"
}

# os.chdir(os.path.join(os.path.abspath(os.sep), "config"))
# cwd = os.getcwd()
# print(f"Current working directory: {cwd}")
# ace_config = dict()
# for file in filter(lambda x: os.path.isfile(x), os.listdir(cwd)):
#     f = open(file)
#     value = f.readlines()[0]
#     ace_config[file] = value
#     f.close()

print(f"Got ace config from secret: {ace_config}")
basic_auth = requests.auth.HTTPBasicAuth(ace_config["user"], ace_config["pw"])

protocol = 'http'
if ace_config["https"] == 'true':
    protocol += 's'
admin_base_url = f'{protocol}://{ace_config["host"]}:{ace_config["port"]}'


def admin_get_request(uri, erc, parse_json, func):
    global admin_base_url
    response = requests.get(f"{admin_base_url}{uri}",
                            auth=basic_auth,
                            verify=False)
    arc = response.status_code
    content = response.content.decode("utf-8")
    if parse_json:
        content = json.loads(content)
    f_content = func(content)
    if arc == erc:
        return f_content
    else:
        print(f"Error")
        print(f"{admin_base_url}{uri} returned code {arc}, expected {erc}")
        print(content)


def admin_post_request(uri, data, erc, parse_json, func):
    global admin_base_url
    response = requests.post(f"{admin_base_url}{uri}",
                            data=data,
                            auth=basic_auth,
                            verify=False)
    arc = response.status_code
    content = response.content.decode("utf-8")
    if parse_json:
        content = json.loads(content)
    f_content = func(content)
    if arc == erc:
        return f_content
    else:
        print(f"Error")
        print(f"{admin_base_url}{uri} returned code {arc}, expected {erc}")
        print(content)


def jsonize(x):
    arr = x.split('-')
    arr[1:] = map(lambda x: x.capitalize(), arr[1:])
    return "".join(arr)


project_types = ("applications", "rest-apis", "services")
data = dict()

# determine which project types are deployed on the ACE server
has_project_types = admin_get_request("/apiv2", 200, True,
                                          lambda x: dict(
                                              (y, x["children"][jsonize(y)]["hasChildren"]) for y in project_types))

# for each project type currently deployed on the ACE server
for project_type in filter(lambda x: has_project_types[x], project_types):
    projects = admin_get_request(f"/apiv2/{project_type}", 200, True,
                                 lambda x: tuple((y["name"], y["uri"]) for y in x["children"]))
    data[project_type] = dict((name, dict()) for name, uri in projects)
    print(project_type)
    # for each project name
    for project_name, project_uri in projects:
        flows = admin_get_request(f"{project_uri}/messageflows", 200, True,
                                  lambda x: tuple((y["name"], y["uri"]) for y in x["children"]))
        data[project_type][project_name] = dict((name, dict()) for name, uri in flows)
        print("\t", project_name)
        # for each flow in the project
        for flow_name, flow_uri in flows:
            recording_on = admin_get_request(f"{flow_uri}", 200, True,
                                              lambda x: "stop-recording" in x["actions"]["available"].keys())
            print("\t" * 2, flow_name, end=": ")

            # if recording is not on
            if not recording_on:
                recording_toggle = admin_post_request(f"{flow_uri}/start-recording", "", 200, False, lambda x: x)
                print("Switched ON")
            else:
                print("Already ON")

