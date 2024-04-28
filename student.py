import json
import logging

import requests
import base64

from requests.cookies import RequestsCookieJar
from starlette import status


class LoginFailedException(Exception):
    def __init__(self, message="Login Failed!"):
        self.message = message
        super().__init__(self.message)


class StudentLoginMethod(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password


class StudentRequest(object):
    def __init__(self, base_url: str, student_login_method: StudentLoginMethod, proxies=None,
                 user_agent: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ('
                                   'KHTML, like Gecko)'
                                   'Chrome/119.0.0.0 Safari/537.36'):
        self.student_user = None
        self.cookies: RequestsCookieJar = RequestsCookieJar()
        self.student_login_method = student_login_method
        self.base_url: str = base_url
        self.session = requests.Session()
        self.proxies = proxies
        self.get_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,'
                      'application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': f'{base_url}/home/login',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
        }
        self.post_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': f'{base_url}',
            'Pragma': 'no-cache',
            'Referer': f'{base_url}/home/login',
            'User-Agent': user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }

    def get_cookies(self):
        try:
            response = self.send_get('', need_login=False)
            result = response.cookies if response is not None else None
            self.cookies = result
            return result
        except requests.exceptions.ConnectionError as err:
            raise err

    def send_get(self, path, need_login=True):
        try:
            if need_login and self.student_user is None:
                if not self.login():
                    logging.error("Login failed")
                    raise LoginFailedException
            response = self.session.get(f'{self.base_url}/{path}', headers=self.get_headers, proxies=self.proxies)
            logging.info(f"GET {response.url} | Status code: {response.status_code}")
            if response.status_code != status.HTTP_200_OK and need_login:
                logging.warning("Received non-200 status code, attempting to re-login and re-send request.")
                if self.login():
                    response = self.session.get(f'{self.base_url}/{path}', headers=self.get_headers,
                                                proxies=self.proxies)
                    logging.info(
                        f"Re-sending GET request after successful re-login. Status code: {response.status_code}")
                else:
                    logging.error("Re-login failed, unable to re-send request.")
            return response
        except requests.exceptions.ConnectionError as err:
            logging.error(f"GET - Path: {path or '[Empty]'}, ERROR: {err}")
            raise err

    def send_post(self, path, data=None, referer=None, need_login=True):
        try:
            if need_login and self.student_user is None:
                if not self.login():
                    logging.error("Login failed")
                    raise LoginFailedException
            headers = self.post_headers
            if referer is not None:
                headers['Referer'] = referer
            response = self.session.post(f'{self.base_url}/{path}', data, headers=headers, proxies=self.proxies)
            logging.info(f"POST {response.url} | Status code: {response.status_code}")
            if response.status_code != status.HTTP_200_OK and need_login:
                logging.warning("Received non-200 status code, attempting to re-login and re-send request.")
                if self.login():
                    response = self.session.post(f'{self.base_url}/{path}', data, headers=headers,
                                                 proxies=self.proxies)
                    logging.info(
                        f"Re-sending POST request after successful re-login. Status code: {response.status_code}")
                else:
                    logging.error("Re-login failed, unable to re-send request.")
            return response
        except requests.exceptions.ConnectionError as err:
            logging.error(f"POST - Path: {path or '[Empty]'}, ERROR: {err}")
            raise err

    def login(self):
        try:
            if self.session is None:
                self.logout()
            if self.cookies is None or len(self.cookies) == 0:
                self.get_cookies()
            self.send_get("interface/getVerifyCode", need_login=False)
            data = {
                'sid': self.student_login_method.username,
                'passWord': base64.b64encode(self.student_login_method.password.encode('utf-8')).decode('utf-8'),
                'verifycode': '',
                'ismobile': '0'
            }
            response = self.send_post("interface/login", data, need_login=False)
            if response.status_code == 200:
                result = json.loads(response.text)
                # print(result)
            else:
                return None
            if result['state'] != 200:
                return None
            self.student_user = StudentUser(result['data']['studentid'], result['data']['token'])
            return StudentUser(result['data']['studentid'], result['data']['token'])
        except requests.exceptions.ConnectionError as err:
            raise err

    def logout(self):
        try:
            self.send_get("home/logout", need_login=False)
            self.student_user = None
            self.session.close()
            self.session = requests.Session()
            self.cookies = None
            return
        except requests.exceptions.ConnectionError as err:
            raise err


class StudentUser(object):
    def __init__(self, student_id, token):
        self.student_id = student_id
        self.token = token

    def get_dict(self):
        return {
            "student_id": self.student_id,
            "token": self.token
        }
