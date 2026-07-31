# ================================================= #
# ************** 安全配置  ************** #
# ================================================= #
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-92_gz8xs7le^0br9=3f$^2ll##y(34z0p^2-r56dos*e)fhi5%'

# ================================================= #
# ************** redis配置，无redis 可不进行配置  ************** #
# ================================================= #
REDIS_PASSWORD = ''
REDIS_HOST = '127.0.0.1'
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:6379'

# ================================================= #
# ************** MySQL数据库配置  ************** #
# ================================================= #
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_admin',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# ================================================= #
# ************** 其他 配置  ************** #
# ================================================= #
# 是否开启演示环境，开启后增 删 改功能失效
DEMO = False
DEBUG = True  # 线上环境请设置为False
ALLOWED_HOSTS = ["*"]
LOGIN_NO_CAPTCHA_AUTH = True  # 登录接口 /api/token/ 是否需要验证码认证，用于测试，正式环境建议取消
ENABLE_LOGIN_ANALYSIS_LOG = True  # 启动登录详细概略获取(通过调用api获取ip详细地址)
