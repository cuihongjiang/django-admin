# -*- coding: utf-8 -*-
"""
接口测试基类：自动登录 + 响应断言助手
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from test.client import Client


class APITestCase(unittest.TestCase):
    """所有接口测试的基类，setUpClass 时以管理员身份登录"""

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.client.login()

    def assertOk(self, resp, msg=''):
        """断言 HTTP 200 且业务 code=2000，返回响应体 dict"""
        try:
            body = resp.json()
        except ValueError:
            self.fail(f'{msg} 非 JSON 响应: http={resp.status_code} text={resp.text[:200]}')
        self.assertEqual(resp.status_code, 200, f'{msg} http={resp.status_code} body={str(body)[:300]}')
        self.assertEqual(body.get('code'), 2000, f'{msg} body={str(body)[:300]}')
        return body

    def assertErr(self, resp, http, code, msg=''):
        """断言错误响应的 HTTP 状态码与业务 code，返回响应体 dict"""
        body = resp.json()
        self.assertEqual(resp.status_code, http, f'{msg} http={resp.status_code} body={str(body)[:300]}')
        self.assertEqual(body.get('code'), code, f'{msg} body={str(body)[:300]}')
        return body
