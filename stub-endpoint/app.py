from flask import Flask, request
app = Flask(__name__)
memory = dict()


@app.route('/stub/register', methods=['POST'])
def register():
    global memory
    stub_id = request.args.get('id')
    memory[stub_id] = request.data
    return f"Stub {stub_id} registered with response", 201


@app.route('/stub/response', methods=['POST'])
def response():
    global memory
    stub_id = request.args.get('id')
    if stub_id in memory.keys():
        ans = memory[stub_id]
        del memory[stub_id]
        return ans, 200
    else:
        return f"Stub {stub_id} does not have an associated response", 404


app.run(host='0.0.0.0', debug=True)
