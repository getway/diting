# ~*~ coding: utf-8 ~*~
#
from __future__ import unicode_literals
import base64
import logging
import uuid

import requests
import ipaddress
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from .models import ViewCount, ViewRecord
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger('diting')


class AdminUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        elif not self.request.user.is_superuser:
            self.raise_exception = True
            return False
        return True


def set_view_count(username, content_type, object_id, access_status="", access_message=''):
    code, message = 400, 'objcet not exit'
    try:
        content_type = ContentType.objects.get(model=content_type)

        model_class = content_type.model_class()
        model_obj = model_class.objects.get(pk=object_id)
        # print(content_type, model_class, model_obj)
    except Exception as e:
        print(e)
        return code, message

    view_status = ViewRecord.objects.create(
        content_type=content_type, object_id=object_id,
        username=username, access_status=access_status,
        access_message=access_message
    )

    view_count, created = ViewCount.objects.get_or_create(content_type=content_type, object_id=object_id)
    view_count.num += 1
    view_count.save()
    code, message = 200, "success"
    # print(view_count, view_status)
    return code, message



