# -*- coding: utf-8 -*-
#

from django.dispatch import receiver
from django.db.models.signals import post_save

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


@receiver(post_save, sender=User)
def on_user_created(sender, instance=None, created=False, **kwargs):
    if created:
        logger.info("Receive user `{}` create signal".format(instance.name))
        from .utils import send_user_created_mail
        logger.info("   - Sending welcome mail ...".format(instance.name))
        if instance.email:
            send_user_created_mail(instance)


# def create_ldap_user(sender, instance, created, **kwargs):
#  if created:
#   new_profile = StudentProfile.objects.create(user=instance)
#   user = LDAPBackend().populate_user(instance.username)
#   if user:
#    desc = user.ldap_user.attrs.get("description", [])[0]
#    office = user.ldap_user.attrs.get("physicalDeliveryOfficeName", [])[0]
#    new_profile.student_number = office
#    new_profile.class_of = desc
#    new_profile.save()