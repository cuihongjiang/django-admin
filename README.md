# Django-Admin 项目架构文档

## 1. 项目概述

这是一个基于 Django + Django REST Framework 构建的企业级后台管理系统，提供完整的 RBAC（基于角色的访问控制）权限管理、用户管理、部门管理、菜单管理等核心功能。

### 1.1 技术栈

- **后端框架**: Django 5.1+
- **API框架**: Django REST Framework
- **认证**: JWT (djangorestframework-simplejwt)
- **缓存**: Redis (django-redis)
- **数据库**: 支持多种关系型数据库（配置在 env.py）
- **日志**: Python logging + RotatingFileHandler
- **文档处理**: openpyxl (Excel 导入导出)

### 1.2 系统特性

- ✅ JWT Token 认证与授权
- ✅ RBAC 权限控制（角色-菜单-按钮）
- ✅ 细粒度数据权限（本人/本部门/本部门及子部门/自定义/全部）
- ✅ 操作日志与登录日志自动记录
- ✅ Redis 缓存优化性能
- ✅ Excel 数据导入导出
- ✅ 系统监控（服务器资源监控）
- ✅ 代码生成器功能

---

## 2. 项目目录结构

```
django-admin/
├── JsAdmin/                    # 核心应用模块
│   ├── apis/                   # API 视图层
│   │   ├── data_dict/         # 数据字典相关接口
│   │   ├── log/               # 日志相关接口
│   │   ├── button.py          # 按钮权限接口
│   │   ├── dept.py            # 部门管理接口
│   │   ├── file.py            # 文件管理接口
│   │   ├── login.py           # 登录认证接口
│   │   ├── menu.py            # 菜单管理接口
│   │   ├── menu_button.py     # 菜单按钮接口
│   │   ├── menu_column.py     # 菜单列权限接口
│   │   ├── monitor.py         # 系统监控接口
│   │   ├── post.py            # 岗位管理接口
│   │   ├── role.py            # 角色管理接口
│   │   └── user.py            # 用户管理接口
│   ├── management/commands/   # Django 自定义管理命令
│   │   ├── generator.py       # 代码生成器命令
│   │   ├── init.py            # 项目初始化命令
│   │   └── init_area.py       # 地区数据初始化
│   ├── serializers/           # 序列化器
│   │   ├── login_serializer.py   # 登录序列化
│   │   └── user_serializers.py   # 用户序列化
│   ├── models.py              # 数据模型定义
│   ├── router.py              # API 路由注册
│   ├── initialize.py          # 数据初始化脚本
│   └── apps.py                # 应用配置
│
├── manageSys/                 # 项目配置目录
│   ├── conf/                  # 配置文件
│   │   └── env.py            # 环境变量配置
│   ├── settings.py           # Django 核心配置
│   ├── urls.py               # 根 URL 配置
│   ├── wsgi.py               # WSGI 入口
│   └── asgi.py               # ASGI 入口
│
├── utils/                     # 工具模块
│   ├── server/               # 服务器监控工具
│   │   ├── linux.py         # Linux 系统监控
│   │   ├── windows.py       # Windows 系统监控
│   │   ├── system.py        # 系统信息获取
│   │   └── public.json      # 公共配置
│   ├── core_initialize.py   # 核心初始化工具
│   ├── js_crud.py           # CRUD 基础操作封装
│   ├── list_to_tree.py      # 列表转树结构工具
│   ├── middleware.py        # 中间件
│   ├── mixins.py            # Mixin 类（数据权限）
│   ├── models.py            # 基础模型类
│   ├── pagination.py        # 分页配置
│   ├── performance.py       # 性能监控
│   ├── permission.py        # 权限控制
│   ├── request_util.py      # 请求工具
│   ├── response_utils.py    # 响应工具
│   ├── system.py            # 系统工具
│   └── usual.py             # 通用工具函数
│
├── docs/                      # 文档目录
│   ├── ARCHITECTURE.md       # 原架构文档
│   └── 项目架构文档.md        # 本文档
│
├── logs/                      # 日志文件目录（运行时生成）
├── manage.py                  # Django 管理脚本
└── .gitignore                # Git 忽略配置
```

---

## 3. 核心架构设计

### 3.1 分层架构

```
┌─────────────────────────────────────────┐
│         前端应用（Vue/React）            │
└─────────────────┬───────────────────────┘
                  │ HTTP/HTTPS
                  ↓
┌─────────────────────────────────────────┐
│         API 层（Django REST Framework）  │
│  ┌─────────────────────────────────┐    │
│  │  认证中间件（JWT）               │    │
│  ├─────────────────────────────────┤    │
│  │  权限中间件（RBAC + 数据权限）   │    │
│  ├─────────────────────────────────┤    │
│  │  日志中间件（操作记录）          │    │
│  ├─────────────────────────────────┤    │
│  │  性能监控中间件                  │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  ViewSet（业务逻辑层）           │    │
│  │  - LoginView                     │    │
│  │  - UserViewSet                   │    │
│  │  - RoleViewSet                   │    │
│  │  - DeptViewSet                   │    │
│  │  - MenuViewSet                   │    │
│  │  - ...                           │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  Serializer（数据验证与转换）    │    │
│  └─────────────────────────────────┘    │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│         数据层（Django ORM）             │
│  ┌─────────────────────────────────┐    │
│  │  Model（数据模型）               │    │
│  │  - Users                         │    │
│  │  - Role                          │    │
│  │  - Dept                          │    │
│  │  - Menu                          │    │
│  │  - MenuButton                    │    │
│  │  - OperationLog                  │    │
│  │  - LoginLog                      │    │
│  │  - ...                           │    │
│  └─────────────────────────────────┘    │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         ↓                 ↓
    ┌─────────┐      ┌─────────┐
    │ 数据库  │      │  Redis  │
    │(MySQL等)│      │  缓存   │
    └─────────┘      └─────────┘
```

### 3.2 核心模块说明

#### 3.2.1 认证与授权模块

**认证机制：**
- 使用 JWT Token 认证（djangorestframework-simplejwt）
- Token 存储在 Redis 中，支持快速验证和过期管理
- Access Token 有效期：1小时（可配置）
- Refresh Token 有效期：1天（可配置）
- 支持 Token 自动轮换机制

**授权机制：**
- 白名单模式：配置在 `settings.WHITE_LIST`
- 基于 DRF 的自定义权限类 `WhitelistOrIsAuthenticated`
- 支持 DEMO 模式（只读访问）

**关键代码位置：**
- 认证视图：`JsAdmin/apis/login.py`
- 权限类：`utils/permission.py`
- 序列化器：`JsAdmin/serializers/login_serializer.py`

#### 3.2.2 RBAC 权限控制模块

**权限模型：**

```
Users（用户）
  ↓ N:N
Role（角色）
  ↓ N:N
  ├── Menu（菜单）
  ├── MenuButton（菜单按钮/接口权限）
  └── MenuColumnField（列表字段权限）
```

**数据权限范围：**
- `0` - 仅本人数据权限
- `1` - 本部门数据权限
- `2` - 本部门及以下数据权限
- `3` - 全部数据权限
- `4` - 自定义数据权限（关联指定部门）

**实现机制：**
- `DataPermissionMixin`：在 ViewSet 中混入，自动过滤查询集
- 缓存优化：用户权限范围缓存在 Redis 中
- 部门树查询：支持递归获取子部门

**关键代码位置：**
- 权限 Mixin：`utils/mixins.py`
- 角色模型：`JsAdmin/models.py - Role`

#### 3.2.3 日志记录模块

**日志类型：**

1. **操作日志（OperationLog）**
   - 记录用户的增删改查操作
   - 包含：请求路径、请求方法、请求参数、响应结果、IP地址、浏览器等

2. **登录日志（LoginLog）**
   - 记录用户登录行为
   - 包含：IP地址、地理位置、浏览器、操作系统等

3. **系统日志**
   - 文件位置：`logs/server.log`、`logs/error.log`
   - 使用 RotatingFileHandler，最大 100MB，保留 5 个备份

**实现机制：**
- 中间件自动拦截：`ApiLoggingMiddleware`
- 异步写入数据库
- 支持配置是否启用：`API_LOG_ENABLE`

**关键代码位置：**
- 日志中间件：`utils/middleware.py`
- 日志模型：`JsAdmin/models.py - OperationLog, LoginLog`

#### 3.2.4 数据模型层

**核心模型基类：CoreModel**

所有业务模型继承自 `CoreModel`，提供统一的审计字段：

```python
- id: 主键（BigAutoField）
- remark: 描述
- creator: 创建人（外键到 Users）
- modifier: 修改人
- belong_dept: 数据归属部门
- update_datetime: 修改时间（自动更新）
- create_datetime: 创建时间（自动添加）
- sort: 显示排序
```

**核心业务模型：**

| 模型名称 | 说明 | 关键字段 |
|---------|------|---------|
| Users | 用户表（继承 AbstractUser） | username, email, mobile, dept, role, post |
| Role | 角色表 | name, code, data_range, menu, permission, column |
| Dept | 部门表（树形结构） | name, parent, owner, phone, status |
| Post | 岗位表 | name, code, status |
| Menu | 菜单表（树形结构） | title, path, component, parent, icon, type |
| MenuButton | 菜单按钮权限表 | menu, name, code, api, method |
| MenuColumnField | 菜单列权限表 | menu, name, code |
| Dict | 数据字典表 | name, code, status |
| DictItem | 字典项表 | label, value, dict |
| CategoryDict | 分类字典表（树形） | label, value, code, parent |
| OperationLog | 操作日志表 | request_path, request_method, request_username |
| LoginLog | 登录日志表 | username, ip, browser, os, city |
| File | 文件管理表 | name, url, size, md5sum |
| Area | 地区表 | name, code, level, pcode |
| ApiWhiteList | 接口白名单表 | url, method, enable_datasource |
| SystemConfig | 系统配置表 | key, value, form_item_type |
| GeneratorTemplate | 代码生成器模板表 | name, code, form_info, table_info |

**关键代码位置：**
- 基础模型：`utils/models.py`
- 业务模型：`JsAdmin/models.py`

#### 3.2.5 工具模块

**CRUD 封装（js_crud.py）**

提供标准化的 CRUD 操作：
- `create()` - 创建
- `batch_create()` - 批量创建
- `update()` - 更新
- `delete()` - 删除
- `retrieve()` - 查询（支持数据权限过滤）
- `export_data()` - 导出 Excel
- `import_data()` - 导入 Excel

**响应工具（response_utils.py）**

统一的响应格式：
```python
ResponseUtils.success(data, msg)  # 成功响应
ResponseUtils.error(msg, code)    # 错误响应
```

**其他工具：**
- `list_to_tree.py` - 列表转树结构（菜单、部门等）
- `usual.py` - 通用工具函数（获取用户信息、部门树等）
- `system.py` - 系统信息获取
- `performance.py` - 性能监控

---

## 4. 配置说明

### 4.1 核心配置（settings.py）

```python
# 自定义用户模型
AUTH_USER_MODEL = 'JsAdmin.Users'

# 权限缓存超时时间（秒）
PERMISSION_CACHE_TIMEOUT = 3600

# 接口白名单
WHITE_LIST = ['/api/login/']

# 接口日志配置
API_LOG_ENABLE = True
API_LOG_METHODS = ['POST', 'GET', 'DELETE', 'PUT', 'PATCH']

# DEMO 模式
DEMO = False

# Redis 缓存配置
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'{REDIS_URL}/1',
        ...
    }
}

# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),      # accessToken 1小时过期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),      # refreshToken 1天过期
    'ROTATE_REFRESH_TOKENS': True,                    # 启用 token 轮换
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    ...
}

# DRF 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'utils.permission.WhitelistOrIsAuthenticated'
    ],
    ...
}
```

### 4.2 环境配置（conf/env.py）

数据库连接、Redis 连接等敏感信息配置在此文件中（未纳入版本控制）。

---

## 5. API 设计

### 5.1 路由注册

所有 API 使用 DRF 的 `DefaultRouter` 统一注册：

```python
# JsAdmin/router.py
api_router = DefaultRouter()
api_router.register(r'login', LoginViewSet, basename='login')
api_router.register(r'user', UserViewSet, basename='user')
api_router.register(r'monitor', MonitorView, basename='monitor')
# ...
```

URL 前缀：`/api/`

### 5.2 API 规范

**请求格式：**
- Content-Type: `application/json`
- Authorization: `Bearer <access_token>`

**响应格式：**

成功响应：
```json
{
    "code": 200,
    "msg": "success",
    "data": { ... }
}
```

错误响应：
```json
{
    "code": 4xx/5xx,
    "msg": "错误信息",
    "data": null
}
```

### 5.3 核心接口列表

| 模块 | 接口路径 | 方法 | 说明 |
|------|---------|------|------|
| 认证 | POST /api/login/ | POST | 用户登录 |
| 认证 | POST /api/login/refresh/ | POST | 刷新 Token |
| 用户 | /api/user/ | GET | 获取用户列表 |
| 用户 | /api/user/ | POST | 创建用户 |
| 用户 | /api/user/{id}/ | GET | 获取单个用户 |
| 用户 | /api/user/{id}/ | PUT | 完整更新用户 |
| 用户 | /api/user/{id}/ | PATCH | 部分更新用户 |
| 用户 | /api/user/{id}/ | DELETE | 删除用户 |
| 用户 | /api/user/{id}/set_password/ | POST | 修改密码（用户自己） |
| 用户 | /api/user/{id}/reset_password/ | PUT | 重置密码（管理员） |
| 角色 | /api/role/ | GET/POST/PUT/DELETE | 角色 CRUD |
| 部门 | /api/dept/ | GET/POST/PUT/DELETE | 部门 CRUD |
| 菜单 | /api/menu/ | GET/POST/PUT/DELETE | 菜单 CRUD |
| 岗位 | /api/post/ | GET/POST/PUT/DELETE | 岗位 CRUD |
| 监控 | /api/monitor/ | GET | 服务器监控 |

---

## 6. 中间件流程

```
请求 Request
    ↓
SecurityMiddleware（安全）
    ↓
SessionMiddleware（会话）
    ↓
CommonMiddleware（通用）
    ↓
CsrfViewMiddleware（CSRF）
    ↓
AuthenticationMiddleware（认证）
    ↓
MessagesMiddleware（消息）
    ↓
XFrameOptionsMiddleware（XFrame）
    ↓
ApiLoggingMiddleware（日志记录）
    ↓
PerformanceMiddleware（性能监控）
    ↓
View 业务逻辑
    ↓
响应 Response
```

---

## 7. 数据初始化

### 7.1 初始化命令

```bash
# 初始化数据（保留已有数据）
python manage.py init

# 强制重新初始化（删除后新增）
python manage.py init -y

# 初始化地区数据
python manage.py init_area
```

### 7.2 初始化内容

`JsAdmin/initialize.py` 包含以下初始化数据：
- 部门数据（示例公司组织架构）
- 菜单数据（系统菜单树）
- 菜单按钮数据（接口权限）
- 角色数据
- 字典数据

---

## 8. 部署建议

### 8.1 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 初始化数据
python manage.py init -y

# 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 8.2 生产环境

**推荐配置：**
- Web 服务器：Nginx
- WSGI 服务器：Gunicorn / uWSGI
- 数据库：PostgreSQL / MySQL
- 缓存：Redis
- 进程管理：Supervisor / systemd

**关键配置：**
- 关闭 DEBUG 模式
- 设置正确的 ALLOWED_HOSTS
- 配置静态文件服务
- 配置 HTTPS
- 配置日志轮转

---

## 9. 安全机制

### 9.1 认证安全

- ✅ JWT Token 过期机制
- ✅ Token 存储在 Redis，支持黑名单
- ✅ 密码加密存储（Django 内置）
- ✅ CSRF 保护

### 9.2 权限安全

- ✅ 接口级别权限控制
- ✅ 数据级别权限控制
- ✅ 超级管理员权限分离
- ✅ 白名单机制

### 9.3 数据安全

- ✅ SQL 注入防护（ORM）
- ✅ XSS 防护
- ✅ 敏感数据脱敏
- ✅ 操作日志完整记录

### 9.4 HTTP 安全

```python
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 10. 性能优化

### 10.1 缓存策略

- ✅ 用户权限范围缓存（Redis）
- ✅ Token 缓存（Redis）
- ✅ 数据库查询优化（select_related / prefetch_related）

### 10.2 数据库优化

- ✅ 合理使用索引（unique, db_index）
- ✅ 外键约束关闭（db_constraint=False）减少数据库负担
- ✅ 使用 CoreModel 统一审计字段

### 10.3 日志优化

- ✅ 日志文件轮转（100MB 自动切割）
- ✅ 异步写入日志
- ✅ 分级别记录（INFO/ERROR）

---

## 11. 扩展指南

### 11.1 添加新模块

1. 在 `JsAdmin/models.py` 中定义模型（继承 CoreModel）
2. 在 `JsAdmin/apis/` 中创建 ViewSet
3. 在 `JsAdmin/router.py` 中注册路由
4. 如需数据权限，混入 `DataPermissionMixin`

### 11.2 添加新接口

```python
# 在对应的 ViewSet 中添加 action
from rest_framework.decorators import action

class UserViewSet(ModelViewSet, DataPermissionMixin):
    @action(detail=False, methods=['get'])
    def custom_action(self, request):
        # 业务逻辑
        return ResponseUtils.success(data)
```

### 11.3 添加新权限

1. 在菜单管理中创建菜单
2. 在菜单按钮管理中添加接口权限
3. 在角色管理中分配权限
4. 系统自动根据角色过滤用户权限

---

## 12. 常见问题

### 12.1 Token 相关问题

**问题**: Token 无效或过期
- 检查 Redis 连接是否正常
- accessToken 过期使用 refreshToken 刷新
- 检查 Token 是否在 Redis 缓存中

**问题**: 刷新 Token 失败
- refreshToken 也有过期时间（默认1天）
- 确保传递正确的 refreshToken
- 检查 SIMPLE_JWT 配置是否正确

### 12.2 数据权限不生效

- 检查 ViewSet 是否混入 `DataPermissionMixin`
- 检查用户角色的 `data_range` 配置
- 检查缓存是否更新

### 12.3 日志未记录

- 检查 `API_LOG_ENABLE` 是否开启
- 检查请求方法是否在 `API_LOG_METHODS` 中
- 检查中间件是否正确配置

---

## 13. 参考资源

- Django 官方文档：https://docs.djangoproject.com/
- Django REST Framework：https://www.django-rest-framework.org/
- djangorestframework-simplejwt：https://django-rest-framework-simplejwt.readthedocs.io/

---

## 14. 版本历史

| 版本 | 日期 | 说明 |
|-----|------|------|
| 1.1 | 2026-01-14 | 添加 Token 刷新接口，优化用户管理接口 |
| 1.0 | 2026-01-13 | 初始版本，完整架构文档 |

---

**文档维护者**: 崔宏江  
**最后更新**: 2026-01-14
