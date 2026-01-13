# -*- coding: utf-8 -*-
# @Time    : 2025/12/7 00:24
# @Author  : 崔宏江
# @FileName: router.py
# @Software: PyCharm
# -*- coding: utf-8 -*-
from JsAdmin.apis.login import LoginView
from JsAdmin.apis.monitor import MonitorView
from JsAdmin.apis.user import UserViewSet
from rest_framework.routers import DefaultRouter

api_router = DefaultRouter()
# # 注册路由
api_router.register(r'login', LoginView, basename='login')
api_router.register(r'monitor', MonitorView, basename='monitor')
api_router.register(r'user', UserViewSet, basename='user')
# api_router.register(r'department', dept_router, basename='department')
# api_router.register(r'position', post_router, basename='position')
# api_router.register(r'menu', menu_router, basename='menu')
# api_router.register(r'role', role_router, basename='role')
# api_router.register(r'button', button_router, basename='button')
# api_router.register(r'menubutton', menu_button_router, basename='menubutton')
# api_router.register(r'dictionary', dict_router, basename='dictionary')
# api_router.register(r'dictitem', dict_item_router, basename='dictitem')
# api_router.register(r'categorydict', category_dict_router, basename='categorydict')
# api_router.register(r'loginlog', login_log_router, basename='loginlog')
# api_router.register(r'operationlog', operation_log_router, basename='operationlog')
# api_router.register(r'file', file_router, basename='file')
# api_router.register(r'menucolumnfield', menu_column_field_router, basename='menucolumnfield')
#
