import requests
import json


class ACEConnection:
    def __init__(self, host: str, admin_port: int, http_port: int, https_port: int, admin_https: bool):
        self.__host = host
        self.__admin_port = admin_port
        self.__admin_protocol = 'http'
        if admin_https:
            self.__admin_protocol += 's'
        self.__http_port = http_port
        self.__https_port = https_port

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

    def __make_request(self, uri, operation, data, expected_rc, parse_json, auth=None, params=None,
                       func=lambda x: x):
        if params is None:
            params = dict()
        response = operation(f"{self.admin_url}{uri}",
                             data=data,
                             auth=auth,
                             params=params,
                             verify=False)
        arc = response.status_code
        content = response.content.decode("utf-8")
        if parse_json:
            content = json.loads(content)
        f_content = func(content)
        if arc == expected_rc:
            return f_content
        else:
            print(f"Error")
            print(f"{operation} {self.admin_url}{uri} returned code {arc}, expected {expected_rc}")
            print(content)

    def get(self, uri, expected_rc, parse_json, auth=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.get, None, expected_rc, parse_json, auth, params, func)

    def post(self, uri, data, expected_rc, parse_json, auth=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.post, data, expected_rc, parse_json, auth, params, func)

    def put(self, uri, data, expected_rc, parse_json, auth=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.put, data, expected_rc, parse_json, auth, params, func)

    def patch(self, uri, data, expected_rc, parse_json, auth=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.patch, data, expected_rc, parse_json, auth, params, func)

    def delete(self, uri, data, expected_rc, parse_json, auth=None, params=None, func=lambda x: x):
        return self.__make_request(uri, requests.delete, data, expected_rc, parse_json, auth, params, func)
