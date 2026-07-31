from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth'
    # django.contrib.auth 已占用 'auth' 标签，这里改用 'jsauth' 避免冲突
    label = 'jsauth'
    verbose_name = '认证登录'
