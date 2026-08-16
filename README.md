# Django-Admin 项目架构文档

## 1. 项目概述

这是一个基于 Django + Django REST Framework 构建的企业级后台管理系统，采用**多应用架构**，提供完整的 RBAC（基于角色的访问控制）权限管理、用户管理、部门管理、菜单管理等核心功能。

### 1.1 技术栈

- **运行环境**: Python 3.12+，使用 [uv](https://docs.astral.sh/uv/) 管理依赖
- **后端框架**: Django 5.2+
- **API框架**: Django REST Framework
- **认证**: JWT (djangorestframework-simplejwt) + Redis 黑名单/用户级失效水位线
- **缓存**: Redis (django-redis)
- **数据库**: MySQL (mysqlclient，连接信息配置在 env.py)
- **API 文档**: drf-spectacular (OpenAPI 3)
- **日志**: Python logging + RotatingFileHandler
- **文档处理**: openpyxl (Excel 导入导出)

### 1.2 系统特性

- ✅ 多应用架构（6 个独立 Django 应用，职责清晰）
- ✅ JWT Token 认证与授权（accessToken/refreshToken 双 token + 轮换）
- ✅ Token 主动吊销：注销当前端（Redis 黑名单）、全端下线（用户级失效水位线）
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
├── apps/                          # 业务应用模块（多应用架构）
│   ├── system/                    # 系统管理应用
│   │   ├── models/                # 数据模型（按业务域拆分）
│   │   │   ├── __init__.py        # 汇总导出所有模型
│   │   │   ├── system.py          # 用户/部门/岗位/角色/菜单/按钮等
│   │   │   ├── area.py            # 地区模型
│   │   │   ├── config.py          # 系统配置/接口白名单
│   │   │   └── generator.py       # 代码生成器模板
│   │   ├── apis/                  # API 视图
│   │   │   ├── user.py            # 用户管理
│   │   │   ├── role.py            # 角色管理
│   │   │   ├── dept.py            # 部门管理
│   │   │   ├── post.py            # 岗位管理
│   │   │   ├── menu.py            # 菜单管理
│   │   │   ├── menu_button.py     # 菜单按钮权限
│   │   │   ├── menu_column.py     # 菜单列权限
│   │   │   └── button.py          # 权限标识
│   │   ├── serializers/           # 序列化器
│   │   │   ├── __init__.py        # 汇总导出
│   │   │   └── user.py            # 用户序列化器（读写分离）
│   │   ├── management/commands/   # 管理命令
│   │   │   ├── init.py            # 项目初始化
│   │   │   ├── init_area.py       # 地区数据初始化
│   │   │   └── generator.py       # 代码生成器
│   │   ├── utils/                 # 系统管理特有工具
│   │   │   ├── permissions.py     # 数据权限 Mixin + get_dept
│   │   │   └── core_initialize.py # 初始化基类
│   │   ├── initialize.py          # 初始化数据脚本
│   │   ├── migrations/            # 数据库迁移
│   │   └── apps.py                # 应用配置
│   │
│   ├── auth/                      # 认证登录应用
│   │   ├── apis/
│   │   │   └── login.py           # 登录/刷新/注销接口
│   │   ├── serializers.py         # 登录序列化器
│   │   └── apps.py                # 应用配置（label=jsauth，避免冲突）
│   │
│   ├── data_dict/                 # 数据字典应用
│   │   ├── models.py              # 字典/字典项/分类字典模型
│   │   ├── apis/                  # 字典/字典项/分类字典接口
│   │   ├── serializers.py         # 字典序列化器
│   │   ├── migrations/
│   │   └── apps.py
│   │
│   ├── log/                       # 日志应用
│   │   ├── models.py              # 操作日志/登录日志模型
│   │   ├── apis/                  # 日志查询/删除接口（只读）
│   │   ├── serializers.py         # 日志序列化器
│   │   ├── migrations/
│   │   └── apps.py
│   │
│   ├── file/                      # 文件管理应用
│   │   ├── models.py              # 文件模型（含 media_file_name）
│   │   ├── apis/
│   │   │   └── file.py            # 文件上传（md5秒传）/下载/预览
│   │   ├── serializers.py         # 文件序列化器
│   │   ├── migrations/
│   │   └── apps.py
│   │
│   ├── monitor/                   # 系统监控应用（无模型）
│   │   ├── apis/
│   │   │   └── monitor.py         # 服务器监控接口
│   │   ├── utils/                 # 监控工具
│   │   │   └── system.py          # 系统信息获取
│   │   └── apps.py
│   │
│   ├── router.py                  # API 路由注册（聚合所有 ViewSet）
│   └── __init__.py
│
├── manageSys/                     # 项目配置目录
│   ├── conf/                      # 分块配置
│   │   ├── env.py                 # 环境配置（SECRET_KEY、数据库、Redis 等）
│   │   ├── drf.py                 # DRF / JWT / API 文档配置
│   │   ├── cache.py               # Redis 缓存配置
│   │   └── log.py                 # 日志配置
│   ├── settings.py                # Django 核心配置（聚合 conf 分块配置）
│   ├── urls.py                    # 根 URL 配置
│   ├── wsgi.py                    # WSGI 入口
│   └── asgi.py                    # ASGI 入口
│
├── utils/                         # 公共工具模块（不依赖任何 app）
│   ├── auth/                      # 认证与权限
│   │   ├── authentication.py      # JWT + Redis 黑名单/水位线认证
│   │   └── permission.py          # 权限控制类
│   ├── web/                       # Web 基础设施
│   │   ├── middleware.py          # 中间件（异常处理、操作日志、性能监控）
│   │   ├── pagination.py          # 分页配置
│   │   ├── request_util.py        # 请求工具（IP、UA、登录日志）
│   │   ├── response_utils.py      # 统一响应工具
│   │   ├── viewsets.py            # ViewSet 基类（CoreModelViewSet）
│   │   └── serializers.py         # 序列化器基类（CoreModelSerializer）
│   ├── db/                        # 数据层基础
│   │   ├── models.py              # CoreModel 基类（审计字段）
│   │   └── js_crud.py             # Excel 导入导出工具
│   ├── common/                    # 通用工具
│   │   ├── list_to_tree.py        # 列表转树结构
│   │   └── usual.py               # 文件操作工具
│   └── monitor/                   # 系统监控（平台实现）
│       ├── system.py              # 系统信息获取入口
│       └── server/                # 分平台实现（linux/windows）
│
├── logs/                          # 日志文件目录（运行时生成）
├── manage.py                      # Django 管理脚本
├── pyproject.toml                 # 项目元信息与依赖声明（uv）
├── uv.lock                        # 依赖锁定文件（uv）
└── .gitignore                     # Git 忽略配置
```

---

## 3. 核心架构设计

### 3.1 多应用架构

项目采用 Django 多应用架构，将业务功能拆分为 6 个独立应用：

| 应用 | 标签 | 职责 | 模型 |
|------|------|------|------|
| `apps.system` | `system` | 系统管理 | Users, Dept, Role, Post, Menu, MenuButton, MenuColumnField, Button, Area, ApiWhiteList, SystemConfig, GeneratorTemplate |
| `apps.auth` | `jsauth` | 认证登录 | 无（仅视图和序列化器） |
| `apps.data_dict` | `data_dict` | 数据字典 | Dict, DictItem, CategoryDict |
| `apps.log` | `log` | 日志管理 | OperationLog, LoginLog |
| `apps.file` | `file` | 文件管理 | File |
| `apps.monitor` | `monitor` | 系统监控 | 无（仅视图） |

> **注意**：`apps.auth` 使用 `label='jsauth'` 避免与 `django.contrib.auth` 的标签冲突。

### 3.2 分层架构

```
┌─────────────────────────────────────────┐
│         前端应用（Vue/React）            │
└─────────────────┬───────────────────────┘
                  │ HTTP/HTTPS
                  ↓
┌─────────────────────────────────────────┐
│         API 层（Django REST Framework）  │
│  ┌─────────────────────────────────┐    │
│  │  中间件层                        │    │
│  │  - ExceptionMiddleware          │    │
│  │  - ApiLoggingMiddleware         │    │
│  │  - PerformanceMiddleware        │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  ViewSet 层（业务逻辑）          │    │
│  │  - LoginViewSet (auth)          │    │
│  │  - UserViewSet (system)         │    │
│  │  - RoleViewSet (system)         │    │
│  │  - DictViewSet (data_dict)      │    │
│  │  - FileViewSet (file)           │    │
│  │  - ...                          │    │
│  └─────────────────────────────────┘    │
│                                          │
│  ┌─────────────────────────────────┐    │
│  │  Serializer 层（数据验证）       │    │
│  └─────────────────────────────────┘    │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│         数据层（Django ORM）             │
│  ┌─────────────────────────────────┐    │
│  │  Model 层（按 app 分组）         │    │
│  │  - system.models                │    │
│  │  - data_dict.models             │    │
│  │  - log.models                   │    │
│  │  - file.models                  │    │
│  └─────────────────────────────────┘    │
└─────────────────┬───────────────────────┘
                  │
         ┌────────┴────────┐
         ↓                 ↓
    ┌─────────┐      ┌─────────┐
    │ 数据库  │      │  Redis  │
    │ (MySQL) │      │  缓存   │
    └─────────┘      └─────────┘
```

### 3.3 核心模块说明

#### 3.3.1 认证与授权模块

**认证机制：**
- 使用 JWT Token 认证（djangorestframework-simplejwt），保持无状态本色
- Access Token 有效期：15分钟（可配置）
- Refresh Token 有效期：1天（可配置）
- 刷新时轮换 refreshToken，旧 refreshToken 自动拉黑

**Token 主动吊销（JWT + Redis）：**
- 单端注销：logout 时将 token 的 jti 写入 Redis 黑名单，TTL 为剩余有效期
- 全端下线：禁用账号/改密码时记录用户级失效水位线，签发时间（iat）早于水位线的 token 全部拒绝
- 每次请求只增加一次 Redis 往返（get_many 同查黑名单和水位线），miss 即放行（fail-open）
- 多端登录互不影响：各端 token 独立，单端退出不影响其他端

**关键代码位置：**
- 认证类与吊销工具：`utils/auth/authentication.py`
- 认证视图：`apps/auth/apis/login.py`
- 权限类：`utils/auth/permission.py`
- 序列化器：`apps/auth/serializers.py`

#### 3.3.2 RBAC 权限控制模块

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

**关键代码位置：**
- 权限 Mixin：`apps/system/utils/permissions.py`（DataPermissionMixin + get_dept）
- 角色模型：`apps/system/models/system.py - Role`

#### 3.3.3 日志记录模块

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

**关键代码位置：**
- 日志中间件：`utils/web/middleware.py`
- 日志模型：`apps/log/models.py`

#### 3.3.4 数据模型层

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

**关键代码位置：**
- 基础模型：`utils/db/models.py`
- 业务模型：`apps/<app>/models/`

#### 3.3.5 工具模块分层

**公共 utils（不依赖任何 app）：**

| 模块 | 内容 |
|------|------|
| `utils/auth/` | JWT 认证 + 权限类 |
| `utils/db/models.py` | CoreModel 基类 |
| `utils/db/js_crud.py` | Excel 导入导出 |
| `utils/web/` | 中间件、请求工具、响应、序列化器、视图集、分页 |
| `utils/common/` | 树形转换、文件工具 |
| `utils/monitor/` | 系统监控（平台实现） |

**app 特有 utils：**

| 模块 | 内容 |
|------|------|
| `apps/system/utils/permissions.py` | DataPermissionMixin + get_dept |
| `apps/system/utils/core_initialize.py` | 初始化基类 |
| `apps/monitor/utils/system.py` | 系统监控（包装 utils.monitor） |

---

## 4. 配置说明

### 4.1 配置组织方式

`settings.py` 采用分块聚合模式，通过 `from .conf.xxx import *` 引入各分块配置：

| 文件 | 职责 |
|------|------|
| `conf/env.py` | SECRET_KEY、数据库、Redis 连接、DEBUG/ALLOWED_HOSTS 等环境配置 |
| `conf/drf.py` | REST_FRAMEWORK、SIMPLE_JWT、SPECTACULAR_SETTINGS |
| `conf/cache.py` | Redis 缓存配置（CACHES） |
| `conf/log.py` | 日志配置（LOGGING、API_LOG_ENABLE 等） |
| `settings.py` | 应用/中间件/路由/模板/认证/国际化等 Django 标准配置 |

### 4.2 核心配置示例

```python
# settings.py —— 应用配置
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'rest_framework_simplejwt',
    # 多应用架构
    'apps.system',
    'apps.data_dict',
    'apps.log',
    'apps.file',
    'apps.monitor',
    'apps.auth',
    'drf_spectacular',
]

# settings.py —— 自定义用户模型
AUTH_USER_MODEL = 'system.Users'

# settings.py —— 项目自定义配置
PERMISSION_CACHE_TIMEOUT = 3600            # 权限缓存超时时间（秒）
WHITE_LIST = ['/api/login/']               # 接口白名单
DEMO = False                               # DEMO 模式

# conf/drf.py —— JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # accessToken 15分钟过期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # refreshToken 1天过期
    'ROTATE_REFRESH_TOKENS': True,                   # 启用 token 轮换
    'BLACKLIST_AFTER_ROTATION': False,               # 轮换拉黑由 Redis 黑名单实现
    'UPDATE_LAST_LOGIN': True,
    ...
}

# conf/drf.py —— DRF 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'utils.auth.authentication.RedisBlacklistJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'utils.auth.permission.WhitelistOrIsAuthenticated'
    ],
    ...
}
```

---

## 5. API 设计

### 5.1 路由注册

所有 API 使用 DRF 的 `DefaultRouter` 统一注册在 `apps/router.py`：

```python
# apps/router.py
api_router = DefaultRouter()
api_router.register(r'login', LoginViewSet, basename='login')
api_router.register(r'user', UserViewSet, basename='user')
api_router.register(r'role', RoleViewSet, basename='role')
api_router.register(r'department', DeptViewSet, basename='department')
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
| 认证 | /api/login/ | POST | 用户登录 |
| 认证 | /api/login/refresh/ | POST | 刷新 Token |
| 认证 | /api/login/logout/ | POST | 退出登录 |
| 用户 | /api/user/ | GET/POST | 用户列表/创建 |
| 用户 | /api/user/{id}/ | GET/PUT/DELETE | 用户详情/更新/删除 |
| 用户 | /api/user/{id}/set_password/ | POST | 修改密码 |
| 用户 | /api/user/{id}/reset_password/ | PUT | 重置密码（管理员） |
| 用户 | /api/user/{id}/set_status/ | PUT | 启用/禁用账号 |
| 角色 | /api/role/ | GET/POST/PUT/DELETE | 角色 CRUD |
| 角色 | /api/role/list/menu/ | GET | 菜单树（授权用） |
| 部门 | /api/department/ | GET/POST/PUT/DELETE | 部门 CRUD |
| 部门 | /api/department/list/tree/ | GET | 部门树 |
| 岗位 | /api/position/ | GET/POST/PUT/DELETE | 岗位 CRUD |
| 岗位 | /api/position/all/export/ | GET | 导出岗位 Excel |
| 岗位 | /api/position/all/import/ | POST | 从 Excel 导入岗位 |
| 菜单 | /api/menu/ | GET/POST/PUT/DELETE | 菜单 CRUD（列表返回树） |
| 菜单 | /api/menu/route/tree/ | GET | 当前用户路由树 |
| 字典 | /api/dictionary/ | GET/POST/PUT/DELETE | 字典 CRUD |
| 字典项 | /api/dictitem/ | GET/POST/PUT/DELETE | 字典项 CRUD |
| 字典项 | /api/dictitem/by/code/ | GET | 按字典编码查字典项 |
| 文件 | /api/file/upload/ | POST | 上传文件（md5 秒传） |
| 文件 | /api/file/{id}/download/ | GET | 下载文件 |
| 监控 | /api/monitor/ | GET | 服务器监控 |

> 所有资源均为标准 DRF ViewSet，同时提供 `all/list`（不分页全量）。列表接口带 `page` 参数时分页，否则返回全量。

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
ExceptionMiddleware（异常处理）
    ↓
ApiLoggingMiddleware（操作日志）
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
# 初始化数据（幂等补齐，保留已有数据）
python manage.py init

# 强制重新初始化（先清空再重建；用户表不会被清空，但会重置页面配置的角色关联）
python manage.py init -y

# 初始化地区数据
python manage.py init_area

# 导出当前库为初始化数据模块（页面调整菜单/按钮/部门/角色/字典后执行并提交）
python manage.py dump_init

# 数据一致性校验（检测悬空引用），加 --fix 清理悬空的按钮/列权限行与多对多残留关联
python manage.py check_data_integrity
```

### 7.2 初始化内容与维护工作流

初始化数据分两部分维护：

- `apps/system/initialize_data.py`、`apps/data_dict/initialize_data.py`
  由 `python manage.py dump_init` 生成，**请勿手工编辑**，包含：
  - 部门数据（示例公司组织架构）
  - 菜单数据（系统菜单树）
  - 菜单按钮数据（接口权限）
  - 权限标识数据
  - 角色数据
  - 字典数据（字典 / 字典项）
- `apps/system/initialize.py` 手工维护超级管理员兜底账号（初始密码 `admin123`，生产环境务必修改）

**维护工作流**：在管理页面上调整了菜单、按钮、部门、角色、字典后，执行
`python manage.py dump_init` 并提交生成的数据文件，保证 `init -y` 重置后数据不回退。
后续在初始化数据中新增记录时，请使用 >= 1000 的 id 段，避免与页面自增 id 冲突。

增量数据修复（如存量数据纠错）请走 Django 数据迁移（`RunPython`），
参考 `apps/system/migrations/0003_fix_permission_data.py`。

---

## 8. 快速开始

### 8.1 开发环境

```bash
# 1. 克隆项目
git clone <repository-url>
cd django-admin

# 2. 安装依赖
uv sync

# 3. 创建数据库
mysql -u root -p -e "CREATE DATABASE django_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. 数据库迁移（迁移文件随仓库分发，直接执行即可）
python manage.py migrate

# 5. 初始化数据
python manage.py init

# 6. 创建超级管理员
python manage.py createsuperuser

# 7. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

### 8.2 生产环境

**推荐配置：**
- Web 服务器：Nginx
- WSGI 服务器：Gunicorn / uWSGI
- 数据库：MySQL / PostgreSQL
- 缓存：Redis
- 进程管理：Supervisor / systemd

**关键配置：**
- 关闭 DEBUG 模式：`DEBUG = False`
- 设置正确的 ALLOWED_HOSTS
- 配置静态文件服务
- 配置 HTTPS
- 配置日志轮转

---

## 9. 安全机制

### 9.1 认证安全

- ✅ JWT Token 过期机制（accessToken 15分钟 / refreshToken 1天）
- ✅ Redis 黑名单：注销/轮换后旧 token 立即失效
- ✅ 用户级失效水位线：禁用账号/改密码后全端立即下线
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
- ✅ 敏感数据脱敏（密码等字段）
- ✅ 操作日志完整记录

### 9.4 HTTP 安全

```python
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 10. 扩展指南

### 10.1 添加新应用

```bash
# 1. 创建应用目录结构
mkdir -p apps/myapp/{models,apis,serializers,migrations}

# 2. 创建 apps.py
class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.myapp'
    label = 'myapp'
    verbose_name = '我的应用'

# 3. 注册应用（settings.py）
INSTALLED_APPS = [
    ...
    'apps.myapp',
]

# 4. 定义模型、视图、序列化器
# 5. 在 apps/router.py 注册路由
```

### 10.2 添加新接口

```python
# 在对应的 ViewSet 中添加 action
from rest_framework.decorators import action

class UserViewSet(ModelViewSet):
    @action(detail=False, methods=['get'])
    def custom_action(self, request):
        # 业务逻辑
        return ResponseUtils.success(data)
```

### 10.3 添加数据权限

```python
# 在 ViewSet 中混入 DataPermissionMixin
from apps.system.utils.permissions import DataPermissionMixin

class MyViewSet(DataPermissionMixin, ModelViewSet):
    data_permission_field = 'belong_dept'  # 部门字段名
    creator_field = 'creator_id'           # 创建者字段名
    ...
```

---

## 11. 常见问题

### 11.1 Token 相关问题

**问题**: Token 无效或过期
- accessToken 过期使用 refreshToken 刷新
- 若提示「token 已被吊销」：该 token 已被注销拉黑，或用户被禁用/改密码触发全端下线，需重新登录
- 检查 Redis 连接是否正常（Redis 故障时吊销检查会 fail-open，不影响正常认证）

**问题**: 刷新 Token 失败
- refreshToken 也有过期时间（默认1天）
- 开启轮换后旧 refreshToken 已拉黑，必须使用最新一次返回的 refreshToken

### 11.2 数据权限不生效

- 检查 ViewSet 是否混入 `DataPermissionMixin`
- 检查用户角色的 `data_range` 配置
- 检查缓存是否更新

### 11.3 日志未记录

- 检查 `API_LOG_ENABLE` 是否开启
- 检查请求方法是否在 `API_LOG_METHODS` 中
- 检查中间件是否正确配置

---

## 12. 参考资源

- Django 官方文档：https://docs.djangoproject.com/
- Django REST Framework：https://www.django-rest-framework.org/
- djangorestframework-simplejwt：https://django-rest-framework-simplejwt.readthedocs.io/
- uv 包管理器：https://docs.astral.sh/uv/

---

## 13. 版本历史

| 版本 | 日期 | 说明 |
|-----|------|------|
| 2.0 | 2026-07-31 | **多应用架构重构**：JsAdmin 拆分为 6 个独立 Django 应用（system/auth/data_dict/log/file/monitor）；utils 模块化重构（公共工具与业务工具分离）；数据库重命名为 django_admin |
| 1.3 | 2026-07-31 | models.py 拆为 models/ 域包、serializers/ 改为域子包（与 apis/ 对齐） |
| 1.2 | 2026-07-31 | 迁移 uv 依赖管理；配置拆分至 conf/ 分块；JWT + Redis 黑名单与用户级全端下线 |
| 1.1 | 2026-01-14 | 添加 Token 刷新接口，优化用户管理接口 |
| 1.0 | 2026-01-13 | 初始版本 |

---

**文档维护者**: 崔宏江
**最后更新**: 2026-07-31
