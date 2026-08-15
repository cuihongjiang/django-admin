# -*- coding: utf-8 -*-
"""
日志模块测试（只读，不动种子数据）：登录日志 / 操作日志
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class LoginLogTest(APITestCase):

    def test_list(self):
        """setUpClass 的登录动作本身就会产生登录日志"""
        body = self.assertOk(self.client.get('/loginlog/'), '登录日志列表')
        self.assertGreaterEqual(len(body['result']), 1)

    def test_detail(self):
        body = self.assertOk(self.client.get('/loginlog/'), '登录日志列表')
        first_id = body['result'][0]['id']
        self.assertOk(self.client.get(f'/loginlog/{first_id}/'), '登录日志详情')

    def test_pagination(self):
        body = self.assertOk(self.client.get('/loginlog/?page=1'), '分页')
        self.assertIn('items', body['result'])


class OperationLogTest(APITestCase):

    def test_list(self):
        body = self.assertOk(self.client.get('/operationlog/'), '操作日志列表')
        self.assertIsInstance(body['result'], list)

    def test_detail_if_exists(self):
        body = self.assertOk(self.client.get('/operationlog/'), '操作日志列表')
        if body['result']:
            self.assertOk(self.client.get(f"/operationlog/{body['result'][0]['id']}/"), '操作日志详情')


if __name__ == '__main__':
    unittest.main()
