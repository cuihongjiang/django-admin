# -*- coding: utf-8 -*-
# @Time    : 2026/7/31
# @Author  : 崔宏江
# @FileName: authentication.py
# @Software: PyCharm
"""
JWT + Redis 黑名单认证

多端登录场景下的 token 主动失效方案：
- 正常请求只做签名校验 + 一次 Redis 查询（miss 即放行，保持 JWT 无状态本色）
- 单 token 吊销（注销当前端）：按 jti 写入黑名单，TTL 为剩余有效期
- 用户级全端下线（禁用账号/改密码）：记录失效水位线时间戳，
  签发时间（iat）早于水位线的 token 全部拒绝
"""
import time

import logging

from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

logger = logging.getLogger(__name__)

# 黑名单缓存 key 前缀，按 jti 记录被吊销的 token
TOKEN_BLACKLIST_PREFIX = 'token_blacklist:'
# 用户级失效水位线 key 前缀，记录该用户 token 的最早可信签发时间
USER_REVOKE_PREFIX = 'user_token_revoked_at:'


def blacklist_token(token):
    """
    将 token 加入 Redis 黑名单
    :param token: 已验证的 Token 对象（AccessToken / RefreshToken）
    """
    jti = token.get('jti')
    exp = token.get('exp')
    if not jti or not exp:
        return
    # TTL 取 token 剩余有效期，过期后黑名单记录自动清理，不占存储
    ttl = int(exp - time.time())
    if ttl > 0:
        cache.set(f'{TOKEN_BLACKLIST_PREFIX}{jti}', 1, timeout=ttl)


def is_token_blacklisted(jti):
    """
    判断 jti 对应的 token 是否已被吊销
    :param jti: token 唯一标识
    :return: bool
    """
    if not jti:
        return False
    return cache.get(f'{TOKEN_BLACKLIST_PREFIX}{jti}') is not None


def revoke_user_tokens(user_id):
    """
    按用户维度吊销全部已签发 token（全端下线）
    记录当前时间为失效水位线，此前签发的 token 全部拒绝；
    TTL 取 refreshToken 最长有效期，之后旧 token 已自然过期，记录自动清理
    :param user_id: 用户 id
    """
    ttl = int(api_settings.REFRESH_TOKEN_LIFETIME.total_seconds())
    # 取整秒与 iat 精度对齐，配合严格小于比较，
    # 避免吊销同一秒内重新登录签发的新 token 被误杀
    cache.set(f'{USER_REVOKE_PREFIX}{user_id}', int(time.time()), timeout=ttl)


def is_token_revoked(payload):
    """
    综合判断 token 是否已失效（一次 Redis 往返查两个 key）：
    1. jti 在黑名单中（单 token 吊销）
    2. 签发时间 iat 早于用户级失效水位线（全端下线）
    :param payload: 已验证的 token payload（支持 Token 对象或 dict）
    :return: bool
    """
    jti = payload.get('jti')
    user_id = payload.get(api_settings.USER_ID_CLAIM)
    blacklist_key = f'{TOKEN_BLACKLIST_PREFIX}{jti}'
    revoke_key = f'{USER_REVOKE_PREFIX}{user_id}'
    values = cache.get_many([blacklist_key, revoke_key])
    # 黑名单命中
    if values.get(blacklist_key) is not None:
        return True
    # 水位线检查：签发时间早于失效时间点即拒绝
    revoked_at = values.get(revoke_key)
    iat = payload.get('iat')
    if revoked_at is not None and iat is not None and iat < revoked_at:
        return True
    return False


class RedisBlacklistJWTAuthentication(JWTAuthentication):
    """
    在标准 JWT 校验（签名/有效期）之后，增加 Redis 吊销检查：
    黑名单（注销/踢人）+ 用户级失效水位线（禁用账号/改密码全端下线），
    使主动吊销的 token 立即失效
    """

    def get_validated_token(self, raw_token):
        validated_token = super().get_validated_token(raw_token)
        if is_token_revoked(validated_token):
            # 已吊销的 token 被使用属安全事件，记录 user_id/jti 便于追溯
            logger.warning('token 已被吊销但仍被使用 user_id=%s jti=%s',
                           validated_token.get(api_settings.USER_ID_CLAIM),
                           validated_token.get('jti'))
            raise InvalidToken('token 已被吊销')
        return validated_token


def get_user_info_from_token(request):
    """
    从请求中获取认证用户
    优先复用 DRF 已认证的 request.user，否则通过带黑名单校验的
    JWT 认证解析 Authorization 头中的 access token，返回对应的用户对象
    :param request: HTTP请求对象
    :return: 用户对象，token 缺失、无效或已吊销时返回 None
    """
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        return user
    result = RedisBlacklistJWTAuthentication().authenticate(request)
    if result is None:
        return None
    user, _ = result
    return user
