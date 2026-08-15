# -*- coding: utf-8 -*-
"""
系统监控测试（只读）
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from test.base import APITestCase


class MonitorTest(APITestCase):

    def test_monitor_info(self):
        """监控接口返回内存/负载数据"""
        body = self.assertOk(self.client.get('/monitor/'), '系统监控')
        result = body['result']
        self.assertIn('mem', result)
        self.assertIn('percent', result['mem'])
        self.assertIn('load_average', result)


if __name__ == '__main__':
    unittest.main()
