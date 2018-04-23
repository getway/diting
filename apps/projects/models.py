#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/6 下午3:44
# @Author  : xiaomao
# @Site    : 
# @File    : models.py
# @Software: PyCharm

from __future__ import unicode_literals
import uuid
from django.db import models
import django.utils.timezone as timezone
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse


class Projects(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(u"项目名", max_length=50)
    dever = models.CharField(u"负责人", max_length=20)
    apps = models.TextField(u"组件", blank=True, default="")
    rely = models.TextField(u"依赖", blank=True, default="")
    date_created = models.DateTimeField(u"添加时间", default=timezone.now, editable=False)
    date_updated = models.DateTimeField(u"修改时间", auto_now=True)
    created_by = models.CharField(max_length=32, null=True, blank=True, verbose_name=_('Created by'))
    groups = models.ManyToManyField('users.UserGroup', related_name='projects_groups', blank=True, verbose_name=_('User group'))
    users = models.ManyToManyField('users.User', related_name='projects_users', blank=True, verbose_name=_('User'))

    def __unicode__(self):
        return self.name

    # @models.permalink
    def get_absolute_url(self):
        return reverse('projects:projects-detail', args=(self.id,))

    # def get_absolute_url(self):
    #     return reverse('users:user-detail', args=(self.id,))