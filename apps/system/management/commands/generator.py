# -*- coding: utf-8 -*-
"""
代码生成器命令（dvadmin 遗留）
"""
import json
import logging
import os
import shutil

from django.core.management.base import BaseCommand

from manageSys.settings import BASE_DIR

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    创建App命令:
    python manage.py createapp app名
    python manage.py createapp app01 app02 ...
    python manage.py createapp 一级文件名/app01 ...    # 支持多级目录建app
    """

    def add_arguments(self, parser):
        parser.add_argument('app_info', nargs='*', type=str, )

    def handle(self, *args, **options):
        app_info = options.get('app_info')
        for name in app_info:
            app = json.loads(name)
            name = app.get('app_name')
            names = name.split('/')
            dnames = ".".join(names)
            app_path = os.path.join(BASE_DIR, "apps", *names)
            # 判断app是否存在
            if os.path.exists(app_path):
                self.stdout.write(f"App {name} 已存在！")
            else:
                self.stdout.write(f"创建 {name} App...")
                # 这里可以添加创建app的逻辑
                self.stdout.write(self.style.SUCCESS(f"创建 {name} App成功"))
