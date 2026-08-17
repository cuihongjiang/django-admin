from django.apps import AppConfig


class SystemAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.system'
    label = 'system'
    verbose_name = '系统管理'

    def ready(self):
        from apps.system import signals
        signals.register()
