import json
import os
import re

from flask import Flask, request
from flask_httpauth import HTTPBasicAuth
from pyace import ACERecord, subdirs_file_content_to_dict, hash_dict_values, create_dir_if_not_exists
from werkzeug.security import check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()

mount_path = os.environ.get('EOD20_INPUTMSGAPI_MOUNT_PATH')
user_dir = os.path.join(mount_path, "users")
data_dir = os.path.join(mount_path, "data")

user_auth = subdirs_file_content_to_dict(user_dir, split_by_line=False)
hash_dict_values(user_auth)
root_trees = ('message', 'localEnvironment', 'environment', 'exceptionList')


def timestamp_to_file(ts):
    """Function to remove 'T' and non-word characters from a timestamp string, effectively rendering a
    'yyyy-MM-ddTHHmmSS.sss formatted timestamp into a yyyyMMddHHmmSSsss timestamp

    :param ts: timestamp
    :type ts: string
    :returns: same string with the non-word characters and 'T' removed."""
    return re.sub(r'[T\W]+', '', ts)


def file_to_timestamp(f):
    """Reverse of timestamp_to_file

    :param f: filename (yyyyMMddHHmmSSsss timestamp)
    :type f: string
    :returns: same string with the format restored"""
    return f"{f[:4]}-{f[4:6]}-{f[6:8]}T{f[8:10]}:{f[10:12]}:{f[12:14]}.{f[14:]}"


def save_inputmsg(record):
    """Saves the four root trees of a record to disk and creates the directories if needed

    :param record: ACERecord instance
    :type record: ACERecord"""
    print("Saving input message:")
    print("=====================")
    save_dir = os.path.join(data_dir, record.integration_server, record.application, record.message_flow,
                            record.source_node, timestamp_to_file(record.timestamp))
    for root_tree in root_trees:
        root_tree_path = os.path.join(save_dir)
        create_dir_if_not_exists(root_tree_path)
        with open(os.path.join(root_tree_path, root_tree), 'w') as f:
            f.write(record.test_data().get(root_tree, ''))
    for key, value in record.test_data().items():
        print(f"{key}: {value}")


def post_messages(req):
    """Logs integration server, poject name, message flow name, input node name and timestamp of each input message,
     and saves each input message to disk.

    :param req: the flask request
    :type req: flas request
    :returns: 201 if input messages are among the payload and have been saved to disk. 204 otherwise."""
    all_records = tuple(ACERecord(elem) for elem in json.loads(req.data))
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
        return {"message": f"Saved {len(inputmsgs)} input messages"}, 201
    else:
        return {"message": "No input messages among payload"}, 204


def get_messages(req):
    """Retrieves (filtered) input message root tree files from disk and assembles them organized per integraion_server,
     project, message_flow name, and input_node and timestamp. URI parameter filters can be applied to select on
     one or more attributes, but they must be additionally specified in the aforementioned order. Timestamp from and
     to URI parameters can be specified to select on timestamp.

     :param req: flask request object
     :type req: flask request
     :returns: a dictionary with server.project.flow.node.timestamp.roottree structure, and a HTTP status code"""
    integration_server = req.args.get('integration_server', '')
    project = req.args.get('project', '')
    message_flow = req.args.get('message_flow', '')
    input_node = req.args.get('input_node', '')
    ts_from = timestamp_to_file(req.args.get('from', ''))
    ts_to = timestamp_to_file(req.args.get('to', '9'))

    specs = [integration_server, project, message_flow, input_node]
    path_filter_string = ''
    for spec in specs:
        if spec == '':
            break
        path_filter_string += (spec + os.path.sep)

    def path_filter(x):
        return x.startswith(path_filter_string) and ts_from <= x.split(os.path.sep)[-1] < ts_to

    payload = subdirs_file_content_to_dict(data_dir, split_by_line=False, subdict_by_path=True, path_filter=path_filter)
    return payload, 200


@auth.verify_password
def verify_password(username, password):
    """Default basic auth verification method"""
    if username in user_auth and check_password_hash(user_auth.get(username), password):
        return username


@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def inputmsg():
    """App route to post or get input messages"""
    if request.method == 'POST':
        return post_messages(request)
    else:
        return get_messages(request)


app.run(host='0.0.0.0', port=8080, debug=True)
