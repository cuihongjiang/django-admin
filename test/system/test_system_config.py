# -*- coding: utf-8 -*-
"""
系统配置管理测试：CRUD + 表驱动开关端到端生效

DEMO 开关经 get_system_config 表驱动读取，WhitelistOrIsAuthenticated 消费：
开启后匿名只读请求（GET/HEAD/OPTIONS）放行。测试结束恢复 DEMO=False。
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import requests  # noqa: E402

from test.base import APITestCase  # noqa: E402
from test.client import BASE_URL  # noqa: E402


class SystemConfigFlowTest(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        body = cls.client.get('/systemconfig/', params={'key': 'DEMO'}).json()
        items = body.get('result') or []
        cls.demo_id = items[0]['id'] if items else None
        assert cls.demo_id, '种子配置 DEMO 不存在，请先执行 migrate'

    @classmethod
    def tearDownClass(cls):
        # 恢复 DEMO=False，避免影响其他用例/线上行为
        if cls.demo_id:
            cls.client.put(f'/systemconfig/{cls.demo_id}/', json={
                'key': 'DEMO', 'title': '演示模式（只读放行）', 'value': False, 'status': True,
            })

    def test_01_crud_and_effect(self):
        # DEMO=False：匿名 GET 被拦截
        status = requests.get(f'{BASE_URL}/menu/', timeout=30).status_code
        self.assertEqual(status, 401, 'DEMO=False 时匿名 GET 应被拦截')

        # 开启 DEMO：匿名只读放行（写操作仍需认证）
        self.assertOk(self.client.put(f'/systemconfig/{self.demo_id}/', json={
            'key': 'DEMO', 'title': '演示模式（只读放行）', 'value': True, 'status': True,
        }), '开启 DEMO')
        status = requests.get(f'{BASE_URL}/menu/', timeout=30).status_code
        self.assertEqual(status, 200, 'DEMO=True 时匿名 GET 应放行')
        status = requests.post(f'{BASE_URL}/menu/', json={}, timeout=30).status_code
        self.assertEqual(status, 401, 'DEMO 只放行只读方法，匿名 POST 应被拦截')

        # 关闭 DEMO：恢复拦截（验证写入后缓存即时失效）
        self.assertOk(self.client.put(f'/systemconfig/{self.demo_id}/', json={
            'key': 'DEMO', 'title': '演示模式（只读放行）', 'value': False, 'status': True,
        }), '关闭 DEMO')
        status = requests.get(f'{BASE_URL}/menu/', timeout=30).status_code
        self.assertEqual(status, 401, 'DEMO=False 后匿名 GET 应恢复拦截')

    def test_02_status_disabled_falls_back(self):
        """status=False 的配置不生效，回退默认值（DEMO 默认 False）"""
        self.assertOk(self.client.put(f'/systemconfig/{self.demo_id}/', json={
            'key': 'DEMO', 'title': '演示模式（只读放行）', 'value': True, 'status': False,
        }), '停用 DEMO 配置')
        status = requests.get(f'{BASE_URL}/menu/', timeout=30).status_code
        self.assertEqual(status, 401, '配置停用时应回退默认值 False')

        # 恢复启用且值为 False
        self.assertOk(self.client.put(f'/systemconfig/{self.demo_id}/', json={
            'key': 'DEMO', 'title': '演示模式（只读放行）', 'value': False, 'status': True,
        }), '恢复 DEMO 配置')


if __name__ == '__main__':
    unittest.main()
