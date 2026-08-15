# -*- coding: utf-8 -*-
"""
认证模块测试：登录 / 刷新 token / 退出登录
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase
from test.client import BASE_URL, Client, USERNAME, PASSWORD


class LoginFlowTest(APITestCase):

    def test_login_success(self):
        """正确账号密码登录成功，返回双 token 和用户信息"""
        c = Client()
        body = c.login()
        self.assertIn('accessToken', body['result'])
        self.assertIn('refreshToken', body['result'])
        self.assertEqual(body['result']['user']['username'], USERNAME)

    def test_login_wrong_password(self):
        """错误密码返回 400"""
        resp = Client().s.post(f'{BASE_URL}/login/', json={'username': USERNAME, 'password': 'wrong'})
        self.assertErr(resp, 400, 400, '错误密码')

    def test_login_missing_field(self):
        """缺少用户名返回 400"""
        resp = self.client.s.post(f'{BASE_URL}/login/', json={'password': 'x'})
        self.assertEqual(resp.status_code, 400, '缺少用户名应 400')

    def test_unauthorized_request(self):
        """无 token 访问受保护接口返回 401"""
        import requests
        resp = requests.get(f'{BASE_URL}/user/', timeout=30)
        self.assertEqual(resp.status_code, 401, '未认证应 401')


class RefreshTokenTest(APITestCase):

    def test_refresh_flow(self):
        """refreshToken 换取新的 accessToken"""
        resp = self.client.post('/login/refresh/', json={'refreshToken': self.client.refresh_token})
        body = self.assertOk(resp, '刷新 token')
        self.assertIn('accessToken', body['result'])
        self.assertIn('refreshToken', body['result'])

    def test_refresh_missing_param(self):
        """缺少 refreshToken 参数返回 400"""
        resp = self.client.post('/login/refresh/', json={})
        self.assertErr(resp, 400, 400, '缺少 refreshToken')

    def test_refresh_invalid_token(self):
        """无效 refreshToken 返回 401"""
        resp = self.client.post('/login/refresh/', json={'refreshToken': 'invalid-token'})
        self.assertErr(resp, 401, 401, '无效 refreshToken')


class LogoutTest(APITestCase):

    def test_logout(self):
        """退出登录成功，且 logout 后原 accessToken 立即失效（黑名单）"""
        c = Client()
        c.login()
        resp = c.post('/login/logout/', json={'refreshToken': c.refresh_token})
        self.assertOk(resp, '退出登录')
        # 退出后原 token 应已被拉黑
        resp2 = c.get('/user/')
        self.assertEqual(resp2.status_code, 401, '退出后原 token 应失效')


if __name__ == '__main__':
    unittest.main()
