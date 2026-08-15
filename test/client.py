# -*- coding: utf-8 -*-
"""
接口测试共享客户端

环境变量可覆盖默认值：
    API_BASE=http://127.0.0.1:8000/api
    API_USER=superadmin
    API_PASSWORD=123456
"""
import os

import requests

BASE_URL = os.environ.get('API_BASE', 'http://127.0.0.1:8000/api')
USERNAME = os.environ.get('API_USER', 'superadmin')
PASSWORD = os.environ.get('API_PASSWORD', '123456')


class Client:
    """已登录的 API 客户端，封装鉴权头和常用方法"""

    def __init__(self, username=USERNAME, password=PASSWORD):
        self.s = requests.Session()
        self.username = username
        self.password = password
        self.access = None
        self.refresh_token = None
        self.user = None

    def login(self):
        resp = self.s.post(f'{BASE_URL}/login/',
                           json={'username': self.username, 'password': self.password},
                           timeout=30)
        body = resp.json()
        assert resp.status_code == 200 and body.get('code') == 2000, f'登录失败: {body}'
        self.access = body['result']['accessToken']
        self.refresh_token = body['result']['refreshToken']
        self.user = body['result']['user']
        return body

    def req(self, method, path, **kw):
        assert self.access, '尚未登录，请先调用 login()'
        headers = kw.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.access}'
        return self.s.request(method, BASE_URL + path, headers=headers, timeout=30, **kw)

    def get(self, path, **kw):
        return self.req('GET', path, **kw)

    def post(self, path, **kw):
        return self.req('POST', path, **kw)

    def put(self, path, **kw):
        return self.req('PUT', path, **kw)

    def delete(self, path, **kw):
        return self.req('DELETE', path, **kw)
