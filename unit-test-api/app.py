from pyace.ace import ACERecord, ACEConnection, ACEConnectionError
from pyace.kube.mountutil import subdirs_file_content_to_dict, hash_dict_values, create_dir_if_not_exists
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
import os
import requests
import json
import time
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

mount_path = os.path.abspath(os.sep)
data_dir = os.path.join(mount_path, "data")
user_dir = os.path.join(mount_path, "users")
ace_config_dir = os.path.join(mount_path, "ace-config")

ace_config = subdirs_file_content_to_dict(ace_config_dir, split_by_line=False)
ace_conn = ACEConnection(
    host=ace_config["host"],
    admin_port=int(ace_config["port"]),
    http_port=7800,
    https_port=7843,
    admin_https=False,
    user=ace_config["user"],
    pw=ace_config["pw"]
)
user_auth = subdirs_file_content_to_dict(user_dir, split_by_line=False)
hash_dict_values(user_auth)

project_types = ('applications', 'services', 'rest-apis')


def invalid_project_tye_msg(proj_type):
    """API return string and HTTP Bad Request (400) issued when project type is not valid.

    Params:
    proj_type: the first path parameter of the Query resource that specifies the ACE project type (applications, services, rest-apis)"""
    return f"Project type {proj_type} is not valid, please use one of the following: {', '.join(project_types)}", 400


def api_response(project_type, result):
    """"Wrapper to return the desired api response only if the specified project type is valid

    Params:
    project_type: the first path parameter (string) of the Query resource that specifies the ACE project type (applications, services, rest-apis)
    result: the desired API response """
    if project_type not in project_types:
        return invalid_project_tye_msg(project_type)
    return result


def process_queries(request, save_dir, replace_allowed):
    """" First checks if the request is a simple dictionary with string keys and string values. If so, the queries in
    the request message are saved to disk

    Params:
    request: the API request object
    save_dir: the directory string ('project_type/project/flow/node/terminal') to which the queries will be saved
    replace_allowed: boolean to indicate PUT (true) or POST (false)"""
    create_dir_if_not_exists(save_dir)
    req_obj = json.loads(request.data)
    result_dict = dict()
    if not all(map(lambda x: all(map(lambda y: isinstance(y, str), x)), req_obj.items())):
        return f"Not all query names or values are strings", 400
    for query_name, query_value in req_obj.items():
        exists = os.path.exists(os.path.join(save_dir, query_name))
        if not replace_allowed and exists:
            result_dict[query_name] = "not created: already exists"
        elif replace_allowed and not exists:
            result_dict[query_name] = "not replaced: does not exist"
        else:
            with open(os.path.join(save_dir, query_name), 'w') as f:
                f.write(query_value)
            result_dict[query_name] = "created"
    if len(os.listdir(save_dir)) == 0:
        os.rmdir(save_dir)
    return result_dict, 200


@auth.verify_password
def verify_password(username, password):
    if username in user_auth and check_password_hash(user_auth.get(username), password):
        return username


class Query(Resource):
    @auth.login_required
    def get(self, project_type, project, msgflow, node, terminal):
        return api_response(project_type, (subdirs_file_content_to_dict(os.path.join(data_dir, project_type, project, msgflow, node, terminal), split_by_line=False, subdict_by_path=True), 200))

    @auth.login_required
    def post(self, project_type, project, msgflow, node, terminal):
        return api_response(project_type, process_queries(request, os.path.join(data_dir, project_type, project, msgflow, node, terminal), False))

    @auth.login_required
    def put(self, project_type, project, msgflow, node, terminal):
        return api_response(project_type, process_queries(request, os.path.join(data_dir, project_type, project, msgflow, node, terminal), True))


def perform_quries(test_payload, project_type, project, msgflow):
    return {'message': 'success'}, 200


class Exerciser(Resource):
    @auth.login_required
    def post(self, project_type, project, msgflow, node):
        result = dict()
        try:
            ace_conn.start_recording(project_type, project, msgflow)
            ace_conn.start_injection(project_type, project, msgflow)
            ace_conn.inject(project_type, project, msgflow, node, request.data)
            time.sleep(1)
            test_payload = ace_conn.get_recorded_test_data()
            result = perform_queries(test_payload, project_type, project, msgflow)
        except ACEConnectionError as e:
            result = {"error": "Something happened before testing completed. Check the logs."}, 500
        finally:
            ace_conn.stop_injection(project_type, project, msgflow)
            ace_conn.stop_recording(project_type, project, msgflow)
            ace_conn.delete_recorded_test_data()
            return result


api.add_resource(Query, '/queries/<string:project_type>/<string:project>/<string:msgflow>/<string:node>/<string:terminal>')
api.add_resource(Exerciser, '/exercise/<string:project_type>/<string:project>/<string:msgflow>/<string:node>')
app.run(host='0.0.0.0', port=8080, debug=True)
