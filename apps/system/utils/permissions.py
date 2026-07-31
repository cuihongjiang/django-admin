# -*- coding: utf-8 -*-
"""
数据权限 Mixin：自动根据用户的数据权限范围过滤查询集
"""
from django.core.cache import cache
from django.conf import settings
from apps.system.models import Users


def get_dept(dept_id: int, dept_all_list=None, dept_list=None):
    """
    递归获取部门的所有下级部门
    :param dept_id: 需要获取的部门id
    :param dept_all_list: 所有部门列表
    :param dept_list: 递归部门list
    :return:
    """
    from apps.system.models import Dept
    if not dept_all_list:
        dept_all_list = Dept.objects.all().values('id', 'parent')
    if dept_list is None:
        dept_list = [dept_id]
    for ele in dept_all_list:
        if ele.get('parent') == dept_id:
            dept_list.append(ele.get('id'))
            get_dept(ele.get('id'), dept_all_list, dept_list)
    return list(set(dept_list))


class DataPermissionMixin:
    """
    用于 ViewSet 的 Mixin，自动根据用户的数据权限范围过滤查询集。
    """
    data_permission_field = 'belong_dept'  # 默认的部门字段名
    creator_field = 'creator_id'           # 默认的创建者字段名

    def get_queryset(self):
        """
        重写 get_queryset，应用数据权限过滤。
        """
        # 获取原始查询集
        queryset = super().get_queryset()

        # 超级管理员不过滤
        if self.request.user.is_superuser:
            return queryset

        # 获取用户的数据权限范围
        data_range = self._get_user_data_range(self.request.user.id)
        user_dept_id = getattr(self.request.user, 'dept_id', None)

        # 根据数据权限范围应用过滤
        if data_range == 0:  # 仅本人数据
            return queryset.filter(**{self.creator_field: self.request.user.id})
        elif data_range == 1:  # 本部门数据
            if user_dept_id:
                return queryset.filter(**{self.data_permission_field: user_dept_id})
            return queryset.none() # 用户无部门，返回空集
        elif data_range == 2:  # 本部门及以下数据
            if user_dept_id:
                dept_and_below_ids = get_dept(user_dept_id)
                return queryset.filter(**{f'{self.data_permission_field}__in': dept_and_below_ids})
            return queryset.none()
        elif data_range == 3:  # 自定义数据权限
            # 获取用户角色关联的部门ID列表
            dept_ids = list(self.request.user.role.values_list('dept__id', flat=True))
            if dept_ids:
                return queryset.filter(**{f'{self.data_permission_field}__in': dept_ids})
            return queryset.none()
        elif data_range == 4:  # 所有数据
            return queryset
        else:  # 默认仅本人数据
            return queryset.filter(**{self.creator_field: self.request.user.id})

    def _get_user_data_range(self, user_id):
        """获取用户的数据权限范围（使用缓存优化）"""
        cache_key = f'user_data_range:{user_id}'
        data_range = cache.get(cache_key)

        if data_range is None:
            try:
                user = Users.objects.get(id=user_id)
                data_range_qs = user.role.values_list('data_range', flat=True)
                data_range = max(list(data_range_qs)) if data_range_qs else 0
                cache.set(cache_key, data_range, timeout=settings.PERMISSION_CACHE_TIMEOUT)
            except Users.DoesNotExist:
                data_range = 0

        return data_range
