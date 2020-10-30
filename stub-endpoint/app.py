from pyace.record import Record
from flask import Flask, request
app = Flask(__name__)
memory = dict()


@app.route('/register', methods=['POST'])
def register():
    global memory
    stub_id = request.args.get('id')
    if stub_id is not None:
        memory[stub_id] = request.data
        return f"Stub {stub_id} registered with response", 201
    else:
        return f"Please use query parameter id (string) to give your mock response a name", 400


@app.route('/response', methods=['POST'])
def response():
    global memory
    stub_id = request.args.get('id')
    if stub_id in memory.keys():
        ans = memory[stub_id]
        del memory[stub_id]
        return ans, 200
    else:
        return f"Stub {stub_id} does not have an associated response", 404


@app.route('/', methods=['GET'])
def index():
    return "Hi!", 200


app.run(host='0.0.0.0', port=8080, debug=True)
