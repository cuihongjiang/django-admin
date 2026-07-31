from django.apps import AppConfig


class DataDictAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data_dict'
    label = 'data_dict'
    verbose_name = '数据字典'
