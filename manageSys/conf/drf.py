# ================================================= #
# ************** DRF / JWT / API文档 配置 ************** #
# ================================================= #
from datetime import timedelta

from .env import SECRET_KEY

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 带 Redis 黑名单校验的 JWT 认证，支持注销/踢人后 token 立即失效
        'utils.auth.authentication.RedisBlacklistJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'utils.auth.permission.WhitelistOrIsAuthenticated'
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'
    ],
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_TYPE_CLAIM': 'token_type',
    'JTI_CLAIM': 'jti',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Django Admin API',
    'DESCRIPTION': 'Django Admin 后台管理系统 API 文档',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
