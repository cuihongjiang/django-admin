# -*- coding: utf-8 -*-
"""
低代码生成器视图集

流程：
1. GET  tables/           查询可生成的模型表
2. POST /api/generator/   保存生成配置（table_info / form_info）
3. POST {id}/code/preview/     预览生成的文件内容
4. GET  {id}/code/download/    下载生成代码 zip 包
5. POST {id}/menu/create/      生成菜单 + 按钮权限（幂等）
"""
import logging

from django.http import HttpResponse
from rest_framework import serializers
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.system.models import GeneratorTemplate, Menu, MenuButton, Role
from apps.system.serializers import GeneratorTemplateSerializer
from utils.generator.builder import build_context, generate_files, generate_zip, to_camel, validate_config
from utils.generator.materialize import materialize_backend
from utils.db.models import get_all_models_objects
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet

logger = logging.getLogger(__name__)


class MenuCreateIn(serializers.Serializer):
    """menu/create 请求体（仅用于接口文档声明）"""
    parent_id = serializers.IntegerField(required=False, help_text='上级菜单 id，缺省为顶级')
    role_ids = serializers.ListField(child=serializers.IntegerField(), required=False,
                                     help_text='需要授权的角色 id 列表')


class GeneratorTemplateViewSet(CoreModelViewSet):
    """
    低代码生成器视图集
    模板配置 CRUD + 代码预览/下载 + 菜单按钮生成
    """
    queryset = GeneratorTemplate.objects.all()
    serializer_class = GeneratorTemplateSerializer
    filter_fields = ['name', 'code', 'has_menu']
    # 全局配置类数据，不做行级数据权限过滤
    apply_data_permission = False

    def _validate(self, request):
        """创建/更新前校验配置 JSON 结构"""
        validate_config(
            request.data.get('table_info', ''),
            request.data.get('form_info', ''),
        )
        if request.data.get('is_new_table') and not (request.data.get('form_info') or []):
            raise ValueError('新建数据表模式至少需要配置一个表单字段')

    def create(self, request, *args, **kwargs):
        try:
            self._validate(request)
        except ValueError as e:
            return ResponseUtils.error(msg=str(e), code=400, status_code=400)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        try:
            self._validate(request)
        except ValueError as e:
            return ResponseUtils.error(msg=str(e), code=400, status_code=400)
        return super().update(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(detail=False, methods=['get'])
    def tables(self, request):
        """
        查询所有可生成的模型表及字段
        GET /api/generator/tables/
        排除 Django 内置应用（auth/contenttypes/admin/sessions）
        """
        result = []
        for model_name, info in get_all_models_objects().items():
            model = info['object']
            app_label = model._meta.app_label
            if app_label in ('auth', 'contenttypes', 'admin', 'sessions'):
                continue
            result.append({
                'model': model_name,
                'app_label': app_label,
                'table_name': info['table']['table'],
                'title': info['table']['tableName'],
                'fields': info['table']['tableFields'],
            })
        return ResponseUtils.success(data=result)

    @extend_schema(request=None, parameters=[
        OpenApiParameter(name='frontend', type=str, location='query',
                         description='前端技术栈：vue（默认）/ react')
    ])
    @action(detail=True, methods=['post'], url_path='code/preview')
    def code_preview(self, request, pk=None):
        """
        预览生成的代码
        POST /api/generator/{id}/code/preview/?frontend=react
        返回 [{path, content}] 文件数组
        """
        template = self.get_object()
        frontend = request.query_params.get('frontend', 'vue')
        if frontend not in ('vue', 'react'):
            return ResponseUtils.error(msg="frontend 仅支持 vue / react", code=400, status_code=400)
        try:
            files = generate_files(template, frontend)
        except Exception:
            logger.exception('代码生成失败 template_id=%s', template.id)
            return ResponseUtils.error(msg="代码生成失败，请检查模板配置", code=500, status_code=500)
        return ResponseUtils.success(data=files, msg=f"共生成 {len(files)} 个文件")

    @extend_schema(request=None, parameters=[
        OpenApiParameter(name='frontend', type=str, location='query',
                         description='前端技术栈：vue（默认）/ react')
    ])
    @action(detail=True, methods=['get'], url_path='code/download')
    def code_download(self, request, pk=None):
        """
        下载生成的代码 zip 包
        GET /api/generator/{id}/code/download/?frontend=react
        """
        template = self.get_object()
        frontend = request.query_params.get('frontend', 'vue')
        if frontend not in ('vue', 'react'):
            return ResponseUtils.error(msg="frontend 仅支持 vue / react", code=400, status_code=400)
        try:
            zip_bytes = generate_zip(template, frontend)
        except Exception:
            logger.exception('代码打包失败 template_id=%s', template.id)
            return ResponseUtils.error(msg="代码打包失败，请检查模板配置", code=500, status_code=500)
        response = HttpResponse(zip_bytes, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{template.code}.zip"'
        return response

    @extend_schema(request=None)
    @action(detail=True, methods=['post'], url_path='backend/create')
    def backend_create(self, request, pk=None):
        """
        落地后端：建数据表 + 写入/复用 序列化器/视图集/路由（幂等，无需人工 copy）
        POST /api/generator/{id}/backend/create/

        - 已有模型的模板：确认模型与路由存在后直接复用
        - 新建数据表的模板：schema_editor 直接建表，代码文件存在即复用
        - 文件写入后开发服务器自动重载生效，生产环境需重启
        """
        template = self.get_object()
        try:
            report = materialize_backend(template)
        except ValueError as e:
            return ResponseUtils.error(msg=str(e), code=400, status_code=400)
        except Exception:
            logger.exception('后端落地失败 template_id=%s', template.id)
            return ResponseUtils.error(msg='后端落地失败，请检查模板配置', code=500, status_code=500)

        if not template.has_backend:
            template.has_backend = True
            template.save(update_fields=['has_backend'])

        reused = all(v != 'created' for v in report.values())
        msg = ('后端已存在，全部复用现有资源' if reused
               else '数据表与后端接口已就绪（开发服务器自动重载后生效，生产环境需重启）')
        return ResponseUtils.success(data=report, msg=msg)

    @extend_schema(request=MenuCreateIn)
    @action(detail=True, methods=['post'], url_path='menu/create')
    def menu_create(self, request, pk=None):
        """
        生成菜单和按钮权限（幂等，重复调用不会重复创建）
        POST /api/generator/{id}/menu/create/
        请求参数: {"parent_id": 1, "role_ids": [1, 2]}
        """
        template = self.get_object()
        context = build_context(template)
        code = context['code']

        parent_id = request.data.get('parent_id')
        role_ids = request.data.get('role_ids') or []

        # 1. 菜单（按 path+component 幂等）
        #    挂在父级目录下时用相对 path，保证前端路由为 /{父路径}/{code}
        menu, menu_created = Menu.objects.get_or_create(
            path=code if parent_id else f'/{code}',
            component=f'/{code}/index',
            defaults={
                'title': template.name or code,
                'name': to_camel(code),
                'icon': 'ant-design:code-outlined',
                'type': 1,
                'status': True,
                'parent_id': parent_id,
                'creator': request.user if getattr(request.user, 'is_authenticated', False) else None,
                'modifier': getattr(request.user, 'username', None),
            },
        )

        # 2. 四个 CRUD 按钮权限（按 menu+api+method 幂等）
        button_defs = [
            ('查询', f'{code}:search', f'/api/{code}/', 0),
            ('新增', f'{code}:add', f'/api/{code}/', 1),
            ('修改', f'{code}:update', f'/api/{code}/{{id}}', 2),
            ('删除', f'{code}:delete', f'/api/{code}/{{id}}', 3),
        ]
        buttons = []
        for name, perm_code, api, method in button_defs:
            button, _ = MenuButton.objects.get_or_create(
                menu=menu, api=api, method=method,
                defaults={
                    'name': name,
                    'code': perm_code,
                    'creator': request.user if getattr(request.user, 'is_authenticated', False) else None,
                    'modifier': getattr(request.user, 'username', None),
                },
            )
            buttons.append(button)

        # 3. 授权给指定角色（超管无需授权天然可见）
        roles = Role.objects.filter(id__in=role_ids)
        for role in roles:
            role.menu.add(menu)
            role.permission.add(*buttons)

        # 4. 标记已生成菜单
        if not template.has_menu:
            template.has_menu = True
            template.save(update_fields=['has_menu'])

        msg = '菜单已生成' if menu_created else '菜单已存在，按钮权限已补全'
        if roles:
            msg += f'，已授权 {len(roles)} 个角色'
        logger.info('生成菜单 menu_id=%s code=%s operator=%s',
                    menu.id, code, getattr(request.user, 'username', None))
        return ResponseUtils.success(data={
            'menu_id': menu.id,
            'button_ids': [b.id for b in buttons],
            'created': menu_created,
        }, msg=msg)
