from django.apps import AppConfig


class MonitorAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.monitor'
    label = 'monitor'
    verbose_name = '服务监控'
