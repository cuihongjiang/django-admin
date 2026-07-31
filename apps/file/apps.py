from django.apps import AppConfig


class FileAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.file'
    label = 'file'
    verbose_name = '文件管理'
