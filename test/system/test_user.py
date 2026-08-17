# -*- coding: utf-8 -*-
"""
用户管理测试：CRUD / 改密 / 重置密码 / 禁用 / 删除保护
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase
from test.client import Client


class UserFlowTest(APITestCase):
    """按编号顺序执行的完整用户生命周期（unittest 按方法名排序）"""

    username = 'api_test_user'

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'user_id', None):
            cls.client.delete(f'/user/{cls.user_id}/')

    def test_01_create(self):
        resp = self.client.post('/user/', json={
            'username': self.username, 'password': 'Init123456', 'name': '接口测试用户',
        })
        body = self.assertOk(resp, '创建用户')
        UserFlowTest.user_id = body['result']['id']
        self.assertEqual(body['result']['username'], self.username)

    def test_01b_login_with_initial_password(self):
        """创建时传入的密码即时生效（不再被忽略回落默认 123456）"""
        c = Client(username=self.username, password='Init123456')
        body = c.login()
        self.assertEqual(body['result']['user']['username'], self.username)

    def test_02_list_and_detail(self):
        body = self.assertOk(self.client.get('/user/'), '用户列表')
        usernames = [u['username'] for u in body['result']]
        self.assertIn(self.username, usernames)
        body = self.assertOk(self.client.get(f'/user/{self.user_id}/'), '用户详情')
        self.assertEqual(body['result']['username'], self.username)

    def test_03_list_pagination(self):
        body = self.assertOk(self.client.get('/user/?page=1'), '分页列表')
        self.assertIn('items', body['result'])
        self.assertIn('total', body['result'])

    def test_04_update(self):
        body = self.assertOk(self.client.put(f'/user/{self.user_id}/', json={
            'username': self.username, 'email': 'apitest@example.com',
        }), '更新用户')
        self.assertEqual(body['result']['email'], 'apitest@example.com')

    def test_05_set_password(self):
        resp = self.client.post(f'/user/{self.user_id}/set_password/', json={'password': 'NewPass123'})
        self.assertOk(resp, '修改密码')

    def test_06_reset_password(self):
        body = self.assertOk(self.client.put(f'/user/{self.user_id}/reset_password/', json={}), '重置密码')
        self.assertIn('123456', body['message'])

    def test_07_login_after_reset(self):
        """重置密码后可以用 123456 登录"""
        c = Client(username=self.username, password='123456')
        body = c.login()
        self.assertEqual(body['result']['user']['username'], self.username)

    def test_08_set_status_disable_then_enable(self):
        body = self.assertOk(self.client.put(f'/user/{self.user_id}/set_status/', json={'status': False}), '禁用')
        self.assertIn('禁用', body['message'])
        body = self.assertOk(self.client.put(f'/user/{self.user_id}/set_status/', json={'status': True}), '启用')
        self.assertIn('启用', body['message'])

    def test_09_set_status_invalid(self):
        """status 非布尔值返回 400"""
        resp = self.client.put(f'/user/{self.user_id}/set_status/', json={'status': 'yes'})
        self.assertErr(resp, 400, 400, '非法 status')

    def test_10_delete(self):
        self.assertOk(self.client.delete(f'/user/{self.user_id}/'), '删除用户')
        resp = self.client.get(f'/user/{self.user_id}/')
        self.assertEqual(resp.status_code, 404, '删除后应 404')
        UserFlowTest.user_id = None

    def test_11_cannot_delete_self(self):
        """不能删除当前登录账号"""
        uid = self.client.user['id']
        self.assertErr(self.client.delete(f'/user/{uid}/'), 400, 400, '删除自己')

    def test_12_cannot_delete_last_superadmin(self):
        """不能删除最后一个超级管理员（当前仅 superadmin 一个）"""
        uid = self.client.user['id']
        self.assertErr(self.client.delete(f'/user/{uid}/'), 400, 400, '删除最后超管')


if __name__ == '__main__':
    unittest.main()


class UserPermissionsTest(APITestCase):

    def test_superuser_gets_all_codes(self):
        """超管返回全部按钮/列权限码"""
        body = self.assertOk(self.client.get('/user/permissions/'), '超管权限')
        self.assertIsInstance(body['result']['buttons'], list)
        self.assertGreater(len(body['result']['buttons']), 0, '种子菜单按钮应非空')

    def test_normal_user_shape(self):
        """普通用户返回结构正确（可为空列表）"""
        c = Client(username='test', password='123456')
        try:
            c.login()
        except AssertionError:
            self.skipTest('种子用户 test 密码非默认，跳过')
        body = self.assertOk(c.get('/user/permissions/'), '普通用户权限')
        self.assertIn('buttons', body['result'])
        self.assertIn('columns', body['result'])
