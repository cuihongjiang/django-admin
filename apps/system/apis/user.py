# -*- coding: utf-8 -*-
"""
用户管理视图集
"""
import logging

from rest_framework.decorators import action
from rest_framework import serializers
from drf_spectacular.utils import extend_schema
from apps.system.models import Users
from apps.system.models.system import MenuButton, MenuColumnField
from apps.system.serializers import SchemaOut, SchemaIn
from utils.auth.authentication import revoke_user_tokens
from utils.web.response_utils import ResponseUtils
from utils.web.viewsets import CoreModelViewSet
from utils.auth.permission import IsAdminOrSuperuser, IsOwnerOrAdmin

logger = logging.getLogger(__name__)


class SetPasswordIn(serializers.Serializer):
    """set_password 请求体（仅用于接口文档声明）"""
    password = serializers.CharField(help_text='新密码')


class ResetPasswordIn(serializers.Serializer):
    """reset_password 请求体（仅用于接口文档声明）"""
    new_password = serializers.CharField(required=False, help_text='预留字段，当前实现固定重置为 123456')


class SetStatusIn(serializers.Serializer):
    """set_status 请求体（仅用于接口文档声明）"""
    status = serializers.BooleanField(help_text='true 启用 / false 禁用')


class UserViewSet(CoreModelViewSet):
    """
    用户管理视图集
    提供用户的 CRUD 操作和密码管理
    继承 CoreModelViewSet 获得统一的分页/全量列表行为，
    create/update/destroy 因涉及密码处理保持自定义
    """
    queryset = Users.objects.all()
    serializer_class = SchemaIn

    def get_serializer_class(self):
        """
        根据操作类型返回不同的序列化器
        读操作使用 SchemaOut，写操作使用 SchemaIn
        """
        if self.action in ['list', 'retrieve']:
            return SchemaOut
        return SchemaIn

    def perform_create(self, serializer):
        """创建用户后的处理"""
        serializer.save()

    def perform_update(self, serializer):
        """更新用户后的处理"""
        serializer.save()

    def create(self, request, *args, **kwargs):
        """创建用户"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        logger.info('创建用户 username=%s operator=%s',
                    serializer.instance.username, getattr(request.user, 'username', None))
        output_serializer = SchemaOut(serializer.instance)
        return ResponseUtils.success(
            data=output_serializer.data,
            msg="用户创建成功"
        )

    def update(self, request, *args, **kwargs):
        """更新用户"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        output_serializer = SchemaOut(serializer.instance)
        return ResponseUtils.success(
            data=output_serializer.data,
            msg="用户更新成功"
        )

    def destroy(self, request, *args, **kwargs):
        """删除用户"""
        instance = self.get_object()

        # 不允许删除自己，否则当前会话立即失去管理者身份
        if instance.id == request.user.id:
            return ResponseUtils.error(msg="不能删除当前登录账号", code=400, status_code=400)

        # 不允许删除最后一个超级管理员，避免系统失去管理入口
        if instance.is_superuser and Users.objects.filter(is_superuser=True).count() <= 1:
            return ResponseUtils.error(msg="不能删除最后一个超级管理员", code=400, status_code=400)

        logger.info('删除用户 username=%s operator=%s',
                    instance.username, getattr(request.user, 'username', None))
        self.perform_destroy(instance)
        return ResponseUtils.success(msg="用户删除成功")

    @extend_schema(request=SetPasswordIn)
    @action(detail=True, methods=["POST"], permission_classes=[IsOwnerOrAdmin])
    def set_password(self, request, pk=None):
        """
        修改密码（用户自己或管理员）
        POST /api/user/{id}/set_password/
        请求参数: {"password": "new_password"}
        """
        instance = self.get_object()
        password = request.data.get("password")
        
        if not password:
            return ResponseUtils.error(
                msg="密码不能为空", 
                code=400, 
                status_code=400
            )

        instance.set_password(password)
        instance.save()
        # 改密码后吊销该用户全部已签发 token，所有端需重新登录
        revoke_user_tokens(instance.id)
        logger.info('修改密码 username=%s operator=%s',
                    instance.username, getattr(request.user, 'username', None))
        return ResponseUtils.success(msg="密码修改成功，请重新登录")

    @extend_schema(request=ResetPasswordIn)
    @action(detail=True, methods=["PUT"], permission_classes=[IsAdminOrSuperuser])
    def reset_password(self, request, pk=None):
        """
        重置密码（仅管理员）
        PUT /api/user/{id}/reset_password/
        将用户密码重置为 123456
        """
        instance = self.get_object()
        default_password = "123456"
        instance.set_password(default_password)
        instance.save()
        # 重置密码后吊销该用户全部已签发 token，所有端需重新登录
        revoke_user_tokens(instance.id)
        logger.info('重置密码 username=%s operator=%s',
                    instance.username, getattr(request.user, 'username', None))
        return ResponseUtils.success(
            msg=f"密码已重置为: {default_password}"
        )

    @extend_schema(request=SetStatusIn)
    @action(detail=True, methods=["PUT"], permission_classes=[IsAdminOrSuperuser])
    def set_status(self, request, pk=None):
        """
        启用/禁用账号（仅管理员）
        PUT /api/user/{id}/set_status/
        请求参数: {"status": true/false}
        禁用时吊销该用户全部已签发 token，所有端立即下线
        """
        instance = self.get_object()
        status = request.data.get("status")

        if not isinstance(status, bool):
            return ResponseUtils.error(
                msg="status 参数必须为布尔值",
                code=400,
                status_code=400
            )

        # status 与 is_active 同步维护，登录校验的是 is_active
        instance.status = status
        instance.is_active = status
        instance.save(update_fields=["status", "is_active"])

        operator = getattr(request.user, 'username', None)
        if not status:
            revoke_user_tokens(instance.id)
            logger.info('禁用账号 username=%s operator=%s', instance.username, operator)
            return ResponseUtils.success(msg="账号已禁用，全端已下线")
        logger.info('启用账号 username=%s operator=%s', instance.username, operator)
        return ResponseUtils.success(msg="账号已启用")

    @extend_schema(request=None)
    @action(detail=False, methods=["GET"])
    def permissions(self, request):
        """
        当前用户的按钮/列权限码
        GET /api/user/permissions/
        超级管理员返回全部；普通用户返回其角色关联的 MenuButton / MenuColumnField code
        """
        user = request.user
        if user.is_superuser:
            buttons = MenuButton.objects.values_list('code', flat=True)
            columns = MenuColumnField.objects.values_list('code', flat=True)
        else:
            roles = user.role.all()
            buttons = MenuButton.objects.filter(role__in=roles).values_list('code', flat=True)
            columns = MenuColumnField.objects.filter(role__in=roles).values_list('code', flat=True)
        return ResponseUtils.success(data={
            "buttons": sorted(set(buttons)),
            "columns": sorted(set(columns)),
        })
