# -*- coding: utf-8 -*-
#

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from common.utils import get_logger
from .models import User
from django_auth_ldap.backend import LDAPBackend
import django_auth_ldap
from django.conf import settings

logger = get_logger(__file__)


#LDAP操作model事件
@receiver(django_auth_ldap.backend.populate_user)
def on_ldap_user_created(sender, **kwargs):
    # print("LDAP监听事件：%s" % kwargs)
    user = kwargs['user']
    user.created_by = 'ldap'
    user.is_ldap_user = 1
    #默认不激活
    # user.is_active = 0


@receiver(post_delete, sender=User)
def on_user_delete(sender, **kwargs):
    username = kwargs['instance'].username
    if settings.AUTH_LDAP:
        try:
            from common.ldapadmin import LDAPTool
            ldap_tool = LDAPTool()
            check_user_code, data = ldap_tool.check_user_status(username)
            if check_user_code != 404:
                status = ldap_tool.ldap_delete(username)
                if status:
                    msg = "用户:%s 删除成功" % username
                    logger.info(msg)
                else:
                    msg = "用户%s 删除失败" % username
                    logger.warning(msg)
        except Exception as e:
            msg = str(e)
            logger.error(msg)


@receiver(post_save, sender=User)
def on_user_created(sender, instance=None, created=False, **kwargs):
    if created:
        logger.info("Receive user `{}` create signal".format(instance.name))
        from .utils import send_user_created_mail
        logger.info("   - Sending welcome mail ...".format(instance.name))
        if instance.email:
            send_user_created_mail(instance)


