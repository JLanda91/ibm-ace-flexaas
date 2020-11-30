import json

import requests


class ACEAdminConnectionError(Exception):
    """Specific error class for ACE connection problems. Contains a default constructor and print"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ACEAdminConnection:
    """Class for ACE connections with Basic auth. Input the server host, admin REST API port, services HTTP port,
    services HTTPS port, admin user and admin pw. This class provides all REST operation methods to make specific
    requests to the admin REST API or the running services."""

    def __init__(self, host: str, admin_port: int, admin_https: bool, user: str, pw: str):
        """Constructor to create an ACE connection instance.

        :param host: host name of the running ACE server
        :type host: string
        :param admin_port: port of the running ACE server
        :type admin_port: string
        :param admin_https: indication whether to use https to connect to the web admin
        :type admin_https: boolean
        :param user: ACE admin username
        :type user: string
        :param pw: ACE admin password
        :type pw: string
        :returns: instance of the class"""
        self.__host = host
        self.__admin_port = admin_port
        self.__admin_protocol = 'https' if admin_https else 'http'
        self.__request_verify = admin_https
        self.__auth = requests.auth.HTTPBasicAuth(user, pw)

    @property
    def admin_url(self):
        """Property holding the admin url, constructed with the class members"""
        return f"{self.__admin_protocol}://{self.__host}:{self.__admin_port}"

    def __make_request(self, uri, operation, data, expected_rc, parse_json, headers=None, params=None,
                       func=lambda x: x):
        """"Generic function to make requests to the admin. The outcome is optionally JSON-parsed and a post-processing
         function can be supplied to extract info from the response. If the expected return code is not returned, an
         ACEAdminConnectionError is raised

        :param uri: ACE admin URI (starts with /apiv2)
        :type uri: string
        :param operation: REST method
        :type operation: function from requests package (requests.get/post/put/patch/delete)
        :param data: ACE admin request payload
        :type data: bytes
        :param expected_rc: expected return code from the request
        :type expected_rc: number
        :param parse_json: indication whether to parse the response as JSON
        :type parse_json: boolean
        :param headers: ACE admin request headers
        :type headers: dictionary
        :param params: ACE admin request parameters
        :type params: dictionary
        :param func: post-processor of the response
        :type func: function
        :returns: the post-processed response content
        :raises: ACEAdminConnectionError"""
        if params is None:
            params = dict()
        url = f"{self.admin_url}{uri}"
        response = operation(url=url, data=data, headers=headers, params=params, auth=self.__auth,
                             verify=self.__request_verify)
        arc = response.status_code
        content = response.content.decode("utf-8")
        if parse_json:
            content = json.loads(content)
        f_content = func(content)
        if arc == expected_rc:
            return f_content
        else:
            raise ACEAdminConnectionError(content)

    def get(self, uri, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        """Specialization of __make_request, specifically for GET requests"""
        return self.__make_request(uri, requests.get, None, expected_rc, parse_json, headers, params, func)

    def post(self, uri, data, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        """Specialization of __make_request, specifically for POST requests"""
        return self.__make_request(uri, requests.post, data, expected_rc, parse_json, headers, params, func)

    def put(self, uri, data, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        """Specialization of __make_request, specifically for PUT requests"""
        return self.__make_request(uri, requests.put, data, expected_rc, parse_json, headers, params, func)

    def patch(self, uri, data, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        """Specialization of __make_request, specifically for PATCH requests"""
        return self.__make_request(uri, requests.patch, data, expected_rc, parse_json, headers, params, func)

    def delete(self, uri, data, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        """Specialization of __make_request, specifically for DELETE requests"""
        return self.__make_request(uri, requests.delete, data, expected_rc, parse_json, headers, params, func)

    def start_recording(self, project_type, project, msgflow):
        """"Specialization of post, to start recording for a specific message flow

        :param project_type: choice of applications/services/rest-apis
        :type project_type: string
        :param project: name of the ACE project
        :type project: string
        :param msgflow: name of the message flow in the project
        :type msgflow: string
        :returns: the response content ("OK") as is
        :raises: ACEAdminConnectionError"""
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/start-recording', None, 200,
                         parse_json=False, headers=None, params=None, func=lambda x: x)

    def stop_recording(self, project_type, project, msgflow):
        """"Specialization of post, to stop recording for a specific message flow

        :param project_type: choice of applications/services/rest-apis
        :type project_type: string
        :param project: name of the ACE project
        :type project: string
        :param msgflow: name of the message flow in the project
        :type msgflow: string
        :returns: the response content ("OK") as is"""
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/stop-recording', None, 200,
                         parse_json=False, headers=None, params=None, func=lambda x: x)

    def start_injection(self, project_type, project, msgflow):
        """"Specialization of post, to start injection for a specific message flow

        :param project_type: choice of applications/services/rest-apis
        :type project_type: string
        :param project: name of the ACE project
        :type project: string
        :param msgflow: name of the message flow in the project
        :type msgflow: string
        :returns: the response content ("OK") as is"""
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/start-injection', None, 200,
                         parse_json=False, headers=None, params=None, func=lambda x: x)

    def stop_injection(self, project_type, project, msgflow):
        """"Specialization of post, to stop injection for a specific message flow

        :param project_type: choice of applications/services/rest-apis
        :type project_type: string
        :param project: name of the ACE project
        :type project: string
        :param msgflow: name of the message flow in the project
        :type msgflow: string
        :returns: the response content ("OK") as is"""
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/stop-injection', None, 200,
                         parse_json=False, headers=None, params=None, func=lambda x: x)

    def inject(self, project_type, project, msgflow, input_node, data):
        """Specialization of post, to inject a message into a message flow

        :param project_type: choice of applications/services/rest-apis
        :type project_type: string
        :param project: name of the ACE project
        :type project: string
        :param msgflow: name of the message flow in the project
        :type msgflow: string
        :param data: payload
        :type data: bytes
        :returns: the response content as is"""
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/nodes/{input_node}/inject', data, 200,
                         parse_json=False, headers={'Content-Type': 'application/json',
                                                    'Accept-Encoding': 'gzip, deflate, br'},
                         params=None, func=lambda x: x)

    def get_recorded_test_data(self):
        """Specialization of get, to obtain the recorded test data from the ACE server

        :returns: the sub-object "recordedTestData"."""
        return self.get(f'/apiv2/data/recorded-test-data', 200, parse_json=True, params=None, func=lambda x:
        x.get("recordedTestData", list()))

    def delete_recorded_test_data(self):
        """Specialization of delete, to delete the recorded test data from the ACE server"""
        return self.delete(f'/apiv2/data/recorded-test-data', None, 204, parse_json=False, params=None,
                           func=lambda x: x)
