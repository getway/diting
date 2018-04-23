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
from django.contrib.auth import authenticate, login as auth_login
from django.utils.translation import ugettext as _
from django.core.cache import cache


logger = logging.getLogger('jumpserver')


class AdminUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        elif not self.request.user.is_superuser:
            self.raise_exception = True
            return False
        return True

