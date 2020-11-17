from pyace.ace import ACERecord
from pyace.kube.mountutil import subdirs_file_content_to_dict, hash_dict_values, create_dir_if_not_exists
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
import os
import requests
import json
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

mount_path = os.path.abspath(os.sep)
mount_path = "C:\\Users\\JLANDA91\\Documents\\eindopdracht-2020\\unit-test-api\\Local"
data_dir = os.path.join(mount_path, "data")
user_dir = os.path.join(mount_path, "users")
ace_config_dir = os.path.join(mount_path, "ace-config")

ace_config = subdirs_file_content_to_dict(ace_config_dir, split_by_line=False)
ace_auth = requests.auth.HTTPBasicAuth(ace_config["user"], ace_config["pw"])
user_auth = subdirs_file_content_to_dict(user_dir, split_by_line=False)
hash_dict_values(user_auth)

project_types = ('applications', 'services', 'rest-apis')


def invalid_project_tye_msg(proj_type):
    return f"Project type {proj_type} is not valid, please use one of the following: {', '.join(project_types)}", 400


def api_response(project_type, result):
    if project_type not in project_types:
        return invalid_project_tye_msg(project_type)
    return result


def process_queries(request, save_dir, replace_allowed):
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


class Exerciser(Resource):
    @auth.login_required
    def post(self, project_type, project, msgflow, node):
        return [project_type, project, msgflow, node], 200


api.add_resource(Query, '/queries/<string:project_type>/<string:project>/<string:msgflow>/<string:node>/<string:terminal>')
api.add_resource(Exerciser, '/exercise/<string:project_type>/<string:project>/<string:msgflow>/<string:node>')
app.run(host='0.0.0.0', port=8080, debug=True)
