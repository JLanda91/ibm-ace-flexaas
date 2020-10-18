from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
import os
import json
import re
from werkzeug.security import generate_password_hash, check_password_hash
from pyace.record import Record

app = Flask(__name__)
auth = HTTPBasicAuth()

users_dir = os.path.join(os.path.abspath(os.sep), "users")
data_dir = os.path.join(os.path.abspath(os.sep), "data")

user_auth = dict()
for users in os.listdir(users_dir):
    user_dir = os.path.join(users_dir, users)
    user = open(os.path.join(user_dir, "user"), "r").readlines()[0]
    pw = open(os.path.join(user_dir, "pw"), "r").readlines()[0]
    user_auth[user] = generate_password_hash(pw)

root_trees = ('message', 'localEnvironment', 'environment', 'exceptionList')


@auth.verify_password
def verify_password(username, password):
    if username in user_auth and check_password_hash(user_auth.get(username), password):
        return username


def timestamp_to_file(ts):
    return ts.replace(" ", "T").replace(":", "_")


def file_to_timestamp(ts):
    return ts.replace("_", ":")


def save_inputmsg(record):
    print("Saving input message:")
    print("=====================")
    save_dir = os.path.join(data_dir, record.integration_server, record.application, record.message_flow,
                            record.source_node)
    filename = timestamp_to_file(record.timestamp)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    with open(os.path.join(save_dir, filename), 'w') as f:
        f.write("\n".join(record.test_data().values()) + "\n")
        for key, value in record.test_data().items():
            print(f"{key}: {value}")


def post_messages(req):
    all_records = tuple(Record(elem) for elem in json.loads(request.data))
    inputmsgs = tuple(filter(lambda x: x.is_first_message, all_records))
    for record in inputmsgs:
        print(f"Integration Server: {record.integration_server}")
        print(f"Project: {record.application}")
        print(f"Message flow: {record.message_flow}")
        print(f"Input node: {record.source_node}")
        print(f"Timestamp: {record.timestamp}")
        save_inputmsg(record)
        print(f"")
    if len(inputmsgs) > 0:
        return f"Saved {len(inputmsgs)} input messages", 201
    else:
        return "No input messages among payload", 204


def get_messages(req):
    integration_server = req.args.get('integration_server', '.+')
    project = req.args.get('project', '.+')
    message_flow = req.args.get('message_flow', '.+')
    input_node = req.args.get('input_node', '.+')
    ts_from = req.args.get('from', '')
    ts_to = req.args.get('to', '9')
    print(ts_from)
    print(ts_to)

    specs = (integration_server, project, message_flow, input_node)
    level_lambdas = tuple(lambda x: re.match(y, x) for y in specs)

    def file_in_range(x):
        return ts_from <= file_to_timestamp(x) < ts_to

    payload = dict()
    for int_s in filter(level_lambdas[0], os.listdir(data_dir)):
        int_s_dir = os.path.join(data_dir, int_s)
        payload[int_s] = dict()
        for proj in filter(level_lambdas[1], os.listdir(int_s_dir)):
            proj_dir = os.path.join(int_s_dir, proj)
            payload[int_s][proj] = dict()
            for flow in filter(level_lambdas[2], os.listdir(proj_dir)):
                flow_dir = os.path.join(proj_dir, flow)
                payload[int_s][proj][flow] = dict()
                for node in filter(level_lambdas[3], os.listdir(flow_dir)):
                    node_dir = os.path.join(flow_dir, node)
                    payload[int_s][proj][flow][node] = dict()
                    for file in filter(file_in_range, os.listdir(node_dir)):
                        f = open(os.path.join(node_dir, file))
                        payload[int_s][proj][flow][node][file_to_timestamp(file)] = dict(
                            (root_tree, line.strip()) for root_tree, line in zip(root_trees, f.readlines()))
                        f.close()
    return payload, 200


@app.route('/inputmsg', methods=['GET', 'POST'])
@auth.login_required
def inputmsg():
    if request.method == 'POST':
        return post_messages(request)
    else:
        return get_messages(request)


app.run(host='0.0.0.0', port=8080, debug=True)
