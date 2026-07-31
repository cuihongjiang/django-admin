# -*- coding: utf-8 -*-
# @Time    : 2025/10/02 17:51
# @Author  : 崔宏江
# @FileName: setting.py
# @Software: PyCharm
from pathlib import Path

# 分块配置：环境/安全、DRF/JWT/API文档、缓存、日志
from .conf.env import *
from .conf.drf import *
from .conf.cache import *
from .conf.log import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ======================================================================
# 环境与调试（默认值兜底，实际值在 conf/env.py 中配置）
# ======================================================================
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

DEBUG = locals().get('DEBUG', True)
ALLOWED_HOSTS = locals().get('ALLOWED_HOSTS', ['*'])
DEMO = locals().get('DEMO', False)


# ======================================================================
# 应用与中间件
# ======================================================================
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    # 添加模块
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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.web.middleware.ExceptionMiddleware',
    'utils.web.middleware.ApiLoggingMiddleware',
    'utils.web.middleware.PerformanceMiddleware',
]


# ======================================================================
# 路由 / 模板 / WSGI
# ======================================================================
ROOT_URLCONF = 'manageSys.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'manageSys.wsgi.application'


# ======================================================================
# 数据库（连接信息在 conf/env.py 中配置）
# ======================================================================
DATABASES = locals().get('DATABASES', {})

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ======================================================================
# 认证与安全
# ======================================================================
AUTH_USER_MODEL = 'system.Users'
USERNAME_FIELD = 'username'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 增加安全头配置
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'


# ======================================================================
# 国际化与时区
# ======================================================================
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False


# ======================================================================
# 静态文件与媒体文件
# ======================================================================
STATIC_URL = 'static/'

# 上传文件存储目录（File 模型 FileField 使用）
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ======================================================================
# 项目自定义配置
# ======================================================================
# 接口白名单，不需要授权直接访问
WHITE_LIST = ['/api/login/']

# 权限缓存有效期（秒）
PERMISSION_CACHE_TIMEOUT = locals().get('PERMISSION_CACHE_TIMEOUT', 3600)

# 继承基础models
ABSTRACT_BASE_CLASSES = True

# 所有app models 对象
ALL_MODELS_OBJECTS = []

# 初始化需要执行的列表，用来初始化后执行
INITIALIZE_RESET_LIST = []
