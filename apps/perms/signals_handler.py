# -*- coding: utf-8 -*-
#

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from common.utils import get_logger


logger = get_logger(__file__)
