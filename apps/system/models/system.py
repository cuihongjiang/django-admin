# -*- coding: utf-8 -*-
"""
系统管理域模型：用户 / 岗位 / 角色 / 部门 / 权限标识 / 菜单 / 菜单权限 / 菜单列字段
"""
from django.db import models
from django.contrib.auth.models import AbstractUser

from utils.db.models import CoreModel


class Users(AbstractUser, CoreModel):
    username = models.CharField(max_length=150, unique=True, db_index=True, verbose_name='用户账号',
                                help_text="用户账号")
    email = models.EmailField(max_length=255, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    mobile = models.CharField(max_length=255, verbose_name="电话", null=True, blank=True, help_text="电话")
    avatar = models.TextField(verbose_name="头像", null=True, blank=True, help_text="头像")
    name = models.CharField(max_length=40, verbose_name="姓名", help_text="姓名")
    status = models.BooleanField(default=True, verbose_name="状态", help_text="状态")
    GENDER_CHOICES = (
        (0, "女"),
        (1, "男"),
    )
    gender = models.IntegerField(choices=GENDER_CHOICES, default=1, verbose_name="性别", null=True, blank=True,
                                 help_text="性别")
    USER_TYPE = (
        (0, "后台用户"),
        (1, "前台用户"),
    )
    user_type = models.IntegerField(choices=USER_TYPE, default=0, verbose_name="用户类型", null=True, blank=True,
                                    help_text="用户类型")
    post = models.ManyToManyField(to='Post', verbose_name='关联岗位', db_constraint=False, help_text="关联岗位")
    role = models.ManyToManyField(to='Role', verbose_name='关联角色', db_constraint=False, help_text="关联角色")
    dept = models.ForeignKey(to='Dept', verbose_name='所属部门', on_delete=models.SET_NULL, db_constraint=False,
                             null=True,
                             blank=True, help_text="关联部门")
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    home_path = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        db_table = "system_users"
        verbose_name = '用户表'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)


class Post(CoreModel):
    name = models.CharField(null=False, max_length=64, verbose_name="岗位名称", help_text="岗位名称")
    code = models.CharField(max_length=32, verbose_name="岗位编码", help_text="岗位编码")
    STATUS_CHOICES = (
        (0, "离职"),
        (1, "在职"),
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="岗位状态", help_text="岗位状态")

    class Meta:
        db_table = "system_post"
        verbose_name = '岗位表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)


class Role(CoreModel):
    name = models.CharField(max_length=64, verbose_name="角色名称", help_text="角色名称")
    code = models.CharField(max_length=64, unique=True, verbose_name="角色编码", help_text="角色编码")
    # key = models.CharField(max_length=64, unique=True, verbose_name="权限字符", help_text="权限字符")
    status = models.BooleanField(default=True, verbose_name="角色状态", help_text="角色状态")
    admin = models.BooleanField(default=False, verbose_name="是否为admin", help_text="是否为admin")
    DATASCOPE_CHOICES = (
        (0, "仅本人数据权限"),
        (1, "本部门数据权限"),
        (2, "本部门及以下数据权限"),
        (3, "全部数据权限"),
        (4, "自定数据权限"),
    )
    data_range = models.IntegerField(default=0, choices=DATASCOPE_CHOICES, verbose_name="数据权限范围",
                                     help_text="数据权限范围")
    dept = models.ManyToManyField(to='Dept', verbose_name='数据权限-关联部门', db_constraint=False,
                                  help_text="数据权限-关联部门")
    menu = models.ManyToManyField(to='Menu', verbose_name='关联菜单', db_constraint=False, help_text="关联菜单")
    permission = models.ManyToManyField(to='MenuButton', verbose_name='关联菜单的接口按钮', db_constraint=False,
                                        help_text="关联菜单的接口按钮")
    column = models.ManyToManyField(to='MenuColumnField', verbose_name='列表权限', db_constraint=False,
                                    help_text="列表权限")

    class Meta:
        db_table = 'system_role'
        verbose_name = '角色表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)


class Dept(CoreModel):
    name = models.CharField(max_length=64, verbose_name="部门名称", help_text="部门名称")
    owner = models.CharField(max_length=32, verbose_name="负责人", null=True, blank=True, help_text="负责人")
    phone = models.CharField(max_length=32, verbose_name="联系电话", null=True, blank=True, help_text="联系电话")
    email = models.EmailField(max_length=32, verbose_name="邮箱", null=True, blank=True, help_text="邮箱")
    status = models.BooleanField(default=True, verbose_name="部门状态", null=True, blank=True,
                                 help_text="部门状态")
    parent = models.ForeignKey(to='Dept', on_delete=models.PROTECT, default=None, verbose_name="上级部门",
                               db_constraint=False, null=True, blank=True, help_text="上级部门")

    class Meta:
        db_table = "system_dept"
        verbose_name = '部门表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)


class Button(CoreModel):
    name = models.CharField(max_length=64, unique=True, verbose_name="权限名称", help_text="权限名称")
    code = models.CharField(max_length=64, unique=True, verbose_name="权限值", help_text="权限值")
    status = models.BooleanField(default=True, verbose_name="按钮状态", null=True, blank=True, help_text="按钮状态")

    class Meta:
        db_table = "system_button"
        verbose_name = '权限标识表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)


class Menu(CoreModel):
    parent = models.ForeignKey(to='Menu', on_delete=models.CASCADE, verbose_name="上级菜单", null=True, blank=True,
                               db_constraint=False, help_text="上级菜单")
    icon = models.CharField(max_length=64, default='ant-design:book-outlined', verbose_name="菜单图标",
                            help_text="菜单图标")
    title = models.CharField(max_length=64, verbose_name="菜单名称", help_text="菜单名称")
    permission = models.CharField(max_length=64, null=True, blank=True, verbose_name="权限标识", help_text="权限标识")
    ISLINK_CHOICES = (
        (0, "否"),
        (1, "是"),
    )
    is_ext = models.BooleanField(default=False, verbose_name="是否外链", help_text="是否外链")

    TYPE_CHOICES = (
        (0, "目录"),
        (1, "菜单"),
    )
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name="是否目录", help_text="是否目录")
    path = models.CharField(max_length=128, verbose_name="路由地址", null=True, blank=True, help_text="路由地址")
    redirect = models.CharField(max_length=128, verbose_name="重定向地址", null=True, blank=True,
                                help_text="重定向地址")

    component = models.CharField(max_length=128, verbose_name="组件地址", null=True, blank=True, help_text="组件地址")
    name = models.CharField(max_length=50, verbose_name="组件名称", null=True, blank=True, help_text="组件名称")
    status = models.BooleanField(default=True, blank=True, verbose_name="菜单状态", help_text="菜单状态")
    keepalive = models.BooleanField(default=False, blank=True, verbose_name="是否页面缓存", help_text="是否页面缓存")
    hide_menu = models.BooleanField(default=False, blank=True, verbose_name="侧边栏中是否隐藏",
                                    help_text="侧边栏中是否隐藏")

    class Meta:
        db_table = "system_menu"
        verbose_name = '菜单表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)


class MenuButton(CoreModel):
    menu = models.ForeignKey(to="Menu", db_constraint=False, related_name="menuPermission", on_delete=models.CASCADE,
                             verbose_name="关联菜单", help_text='关联菜单')
    name = models.CharField(max_length=64, verbose_name="名称", help_text="名称")
    code = models.CharField(max_length=64, verbose_name="权限值", help_text="权限值")
    api = models.CharField(max_length=200, verbose_name="接口地址", help_text="接口地址")
    METHOD_CHOICES = (
        (0, "GET"),
        (1, "POST"),
        (2, "PUT"),
        (3, "DELETE"),
    )
    method = models.IntegerField(default=0, verbose_name="接口请求方法", null=True, blank=True,
                                 help_text="接口请求方法")

    class Meta:
        db_table = "system_menu_button"
        verbose_name = '菜单权限表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)


class MenuColumnField(CoreModel):
    menu = models.ForeignKey(to="Menu", db_constraint=False, related_name="menuColumnField", on_delete=models.CASCADE,
                             verbose_name="关联菜单", help_text='关联菜单')
    name = models.CharField(max_length=64, verbose_name="名称", help_text="名称")
    code = models.CharField(max_length=64, verbose_name="权限值", help_text="权限值")

    class Meta:
        db_table = "system_menu_column_field"
        verbose_name = '菜单数据列表'
        verbose_name_plural = verbose_name
        ordering = ('sort',)
