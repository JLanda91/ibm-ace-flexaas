from pyace.ace import ACERecord
from pyace.kube.mountutil import subdirs_file_content_to_dict, hash_dict_values
from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, Api
import os
import requests
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

mount_path = os.path.abspath(os.sep)
data_dir = os.path.join(mount_path, "data")
user_dir = os.path.join(mount_path, "users")
ace_config_dir = os.path.join(mount_path, "ace-config")

ace_config = subdirs_file_content_to_dict(ace_config_dir, split_by_line=False)
ace_auth = requests.auth.HTTPBasicAuth(ace_config["user"], ace_config["pw"])
user_auth = subdirs_file_content_to_dict(user_dir, split_by_line=False)
hash_dict_values(user_auth)


@auth.verify_password
def verify_password(username, password):
    if username in user_auth and check_password_hash(user_auth.get(username), password):
        return username


class RootQuery(Resource):
    @auth.login_required
    def get(self, project_type, project, msgflow, node, terminal, query_name):
        return {'project_type': project_type, 'project': project, 'msgflow': msgflow, "node": node, "terminal": terminal, "query_name": query_name}

    @auth.login_required
    def post(self, project_type, project, msgflow, node, terminal, query_name):
        pass

    @auth.login_required
    def put(self, project_type, project, msgflow, node, terminal, query_name):
        pass


api.add_resource(RootQuery, '/<string:project_type>/<string:project>/<string:msgflow>/<string:node>/<string:terminal>/<string:query_name>')
app.run(host='0.0.0.0', port=8080, debug=True)
