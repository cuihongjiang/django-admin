# -*- coding: utf-8 -*-
"""
数据权限（DataPermissionMixin）行为测试

用户无角色时 data_range=0（仅本人数据）：普通用户 list 只能看到自己创建的数据，
超级管理员不受限。以公告（/api/notice/，业务表默认启用数据权限）为样本。
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase  # noqa: E402
from test.client import Client  # noqa: E402


class DataPermissionFlowTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 清理历史残留的同名测试用户（setUpClass 中途失败时 tearDownClass 不会执行）
        for item in cls.client.get('/user/').json().get('result') or []:
            if item.get('username') in ('dp_test_a', 'dp_test_b'):
                cls.client.delete(f"/user/{item['id']}/")
        cls.user_a = cls._create_user('dp_test_a')
        cls.user_b = cls._create_user('dp_test_b')
        cls.client_a = Client(username='dp_test_a', password='Init123456')
        cls.client_a.login()
        cls.client_b = Client(username='dp_test_b', password='Init123456')
        cls.client_b.login()

    @classmethod
    def _create_user(cls, username):
        body = cls.client.post('/user/', json={
            'username': username, 'password': 'Init123456', 'name': username,
        }).json()
        assert body.get('code') == 2000, f'创建用户失败: {body}'
        return body['result']['id']

    @classmethod
    def tearDownClass(cls):
        for notice_id in getattr(cls, 'notice_ids', []):
            cls.client.delete(f'/notice/{notice_id}/')
        for user_id in (cls.user_a, cls.user_b):
            cls.client.delete(f'/user/{user_id}/')

    def test_01_owner_only_visibility(self):
        """data_range=0：普通用户只能看到自己创建的数据"""
        body_a = self.assertOk(self.client_a.post('/notice/', json={
            'title': '数据权限测试-A', 'content': 'a', 'status': True,
        }), 'A 创建公告')
        body_b = self.assertOk(self.client_b.post('/notice/', json={
            'title': '数据权限测试-B', 'content': 'b', 'status': True,
        }), 'B 创建公告')
        DataPermissionFlowTest.notice_ids = [body_a['result']['id'], body_b['result']['id']]

        list_a = self.assertOk(self.client_a.get('/notice/'), 'A 查看列表')['result']
        titles_a = {item['title'] for item in list_a}
        self.assertIn('数据权限测试-A', titles_a, 'A 应能看到自己的数据')
        self.assertNotIn('数据权限测试-B', titles_a, 'A 不应看到 B 的数据')

        list_b = self.assertOk(self.client_b.get('/notice/'), 'B 查看列表')['result']
        titles_b = {item['title'] for item in list_b}
        self.assertIn('数据权限测试-B', titles_b, 'B 应能看到自己的数据')
        self.assertNotIn('数据权限测试-A', titles_b, 'B 不应看到 A 的数据')

    def test_02_superuser_unfiltered(self):
        """超级管理员不受数据权限限制"""
        list_all = self.assertOk(self.client.get('/notice/'), '管理员查看列表')['result']
        titles = {item['title'] for item in list_all}
        self.assertIn('数据权限测试-A', titles)
        self.assertIn('数据权限测试-B', titles)

    def test_03_management_table_excluded(self):
        """全局配置类接口（菜单）对普通用户不做数据权限过滤"""
        body = self.assertOk(self.client_a.get('/menu/'), 'A 查看菜单')
        self.assertTrue(body['result'], '普通用户应能看到菜单配置数据')


if __name__ == '__main__':
    unittest.main()
