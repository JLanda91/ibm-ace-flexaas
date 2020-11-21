import requests
import json


class ACEConnectionError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ACEConnection:
    def __init__(self, host: str, admin_port: int, http_port: int, https_port: int, admin_https: bool, user: str,
                 pw: str):
        self.__host = host
        self.__admin_port = admin_port
        self.__admin_protocol = 'http'
        self.__request_verify = admin_https
        if admin_https:
            self.__admin_protocol += 's'
        self.__http_port = http_port
        self.__https_port = https_port
        self.__auth = requests.auth.HTTPBasicAuth(user, pw)

    @property
    def admin_url(self):
        return f"{self.__admin_protocol}://{self.__host}:{self.__admin_port}"

    @property
    def admin_rest_url(self):
        return f"{self.admin_url}/apiv2"

    @property
    def http_url(self):
        return f"http://{self.__host}:{self.__http_port}"

    @property
    def https_url(self):
        return f"https://{self.__host}:{self.__https_port}"

    def __make_request(self, uri, operation, data, expected_rc, parse_json, headers=None, params=None,
                       func=lambda x: x):
        if params is None:
            params = dict()
        url = f"{self.admin_url}{uri}"
        response = operation(url=url,
                             data=data,
                             headers=headers,
                             params=params,
                             auth=self.__auth,
                             verify=self.__request_verify)
        arc = response.status_code
        content = response.content.decode("utf-8")
        if parse_json:
            content = json.loads(content)
        f_content = func(content)
        if arc == expected_rc:
            return f_content
        else:
            raise ACEConnectionError(content)

    def get(self, uri, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.get, None, expected_rc, parse_json, headers, params, func)

    def post(self, uri, data, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.post, data, expected_rc, parse_json, headers, params, func)

    def put(self, uri, data, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.put, data, expected_rc, parse_json, headers, params, func)

    def patch(self, uri, data, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.patch, data, expected_rc, parse_json, headers, params, func)

    def delete(self, uri, data, expected_rc, parse_json, headers=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.delete, data, expected_rc, parse_json, headers, params, func)

    def start_recording(self, project_type, project, msgflow):
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/start-recording', None, 200,
                         parse_json=False, headers=None, params=None, func=lambda x: x)

    def stop_recording(self, project_type, project, msgflow):
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/stop-recording', None, 200,
                         parse_json=False, headers=None, params=None, func=lambda x: x)

    def start_injection(self, project_type, project, msgflow):
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/start-injection', None, 200,
                         parse_json=False, headers=None, params=None, func=lambda x: x)

    def stop_injection(self, project_type, project, msgflow):
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/stop-injection', None, 200,
                         parse_json=False, headers=None, params=None, func=lambda x: x)

    def inject(self, project_type, project, msgflow, input_node, data):
        return self.post(f'/apiv2/{project_type}/{project}/messageflows/{msgflow}/nodes/{input_node}/inject', data, 200,
                         parse_json=False, headers={'Content-Type': 'application/json',
                                                    'Accept-Encoding': 'gzip, deflate, br'},
                         params=None, func=lambda x: x)

    def get_recorded_test_data(self):
        return self.get(f'/apiv2/data/recorded-test-data', 200, parse_json=True, params=None, func=lambda x:
                        x.get("recordedTestData", list()))

    def delete_recorded_test_data(self):
        return self.delete(f'/apiv2/data/recorded-test-data', None, 204, parse_json=False, params=None,
                           func=lambda x: x)
