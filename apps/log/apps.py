from django.apps import AppConfig


class LogAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.log'
    label = 'log'
    verbose_name = '日志管理'
