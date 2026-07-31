# ================================================= #
# ************** 缓存 配置 ************** #
# ================================================= #
from .env import REDIS_URL

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f'{REDIS_URL}/1',
        "TIMEOUT": None,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
}
