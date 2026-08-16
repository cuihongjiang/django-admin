# -*- coding: utf-8 -*-
"""
初始化基类：用于系统数据初始化
"""
import logging

from manageSys import settings

logger = logging.getLogger(__name__)


class CoreInitialize:
    """
    使用方法：继承此类，重写 run方法，在 run 中调用 save 进行数据初始化
    """
    creator_id = None
    reset = False

    def __init__(self, reset=False, creator_id=None):
        """
        reset: 是否重置初始化数据
        creator_id: 创建人id
        """
        self.reset = reset or self.reset
        self.creator_id = creator_id or self.creator_id

    def save(self, obj, data: list, name=None, no_reset=False):
        name = name or obj._meta.verbose_name
        logger.info('正在初始化[%s => %s]', obj._meta.label, name)
        if not no_reset and self.reset and obj not in settings.INITIALIZE_RESET_LIST:
            try:
                obj.objects.all().delete()
                settings.INITIALIZE_RESET_LIST.append(obj)
            except Exception:
                logger.warning('清空旧数据失败[%s]', obj._meta.label, exc_info=True)
        for ele in data:
            m2m_dict = {}
            new_data = {}
            for key, value in ele.items():
                # 判断传的 value 为 list 的多对多进行抽离，使用 set 进行更新
                if isinstance(value, list):
                    m2m_dict[key] = value
                else:
                    new_data[key] = value
            object, _ = obj.objects.get_or_create(id=ele.get("id"), defaults=new_data)
            for key, values in m2m_dict.items():
                values = [value for value in set(values) if value]
                if values:
                    relation = getattr(object, key)
                    # 与已有关联合并（只增不减），保持多次初始化幂等
                    existing = set(relation.values_list('id', flat=True))
                    relation.set(existing | set(values))
        logger.info('初始化完成[%s => %s]', obj._meta.label, name)

    def run(self):
        raise NotImplementedError('.run() must be overridden')
