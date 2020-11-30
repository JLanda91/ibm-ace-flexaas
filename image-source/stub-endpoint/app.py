from flask import Flask, request

app = Flask(__name__)
memory = dict()


@app.route('/register', methods=['POST'])
def register():
    """"App route method for registering mock responses under a key named 'id', which must be used as a URL parameter.
    Stores the request data into the in-memory dictionary of mock responses under key=id.

    :returns: 201 if ?id= was included in the request, 400 if otherwise"""
    global memory
    stub_id = request.args.get('id')
    if stub_id is not None:
        memory[stub_id] = request.data
        return {"message": f"Stub {stub_id} registered with response"}, 201
    else:
        return {"error": f"Please use query parameter id (string) to give your mock response a name"}, 400


@app.route('/response', methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE'])
def response():
    """"App route method for issuing mock responses under a key named 'id', which must be used as a URL parameter.
    Returns the mock responses in-memory dictionary value under key=id. Deletes the mock response from the dictionary.

    :returns: 200 if ?id= was included in the request and occurs in the dictionary, 404 if otherwise"""
    global memory
    stub_id = request.args.get('id')
    if stub_id in memory.keys():
        ans = memory[stub_id]
        del memory[stub_id]
        return ans, 200
    else:
        return {"error": f"Stub {stub_id} does not have an associated response"}, 404


@app.route('/', methods=['DELETE'])
def index():
    """"App route method for clearing the in-memory mock responses dictionary.

    :returns: 200 always"""
    memory.clear()
    return {"message": "Stubs cleaned"}, 200


app.run(host='0.0.0.0', port=8081, debug=True)
