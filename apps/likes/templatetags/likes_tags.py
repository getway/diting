#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/10 上午10:50
# @Author  : xiaomao
# @Site    : 
# @File    : likes_tags.py
# @Software: PyCharm

from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import LikeCount, LikeRecord, ViewRecord, ViewCount


register = template.Library()


@register.simple_tag
def get_like_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=obj.pk)
    return like_count.liked_num


@register.simple_tag
def get_view_count(obj):
    content_type = ContentType.objects.get_for_model(obj)
    view_count, created = ViewCount.objects.get_or_create(content_type=content_type, object_id=obj.pk)
    return view_count.num


@register.simple_tag(takes_context=True)
def get_like_status(context, obj):
    content_type = ContentType.objects.get_for_model(obj)
    user = context['user']
    if not user.is_authenticated:
        return ''
    if LikeRecord.objects.filter(content_type=content_type, object_id=obj.pk, user=user).exists():
        return 'active'
    else:
        return ''


@register.simple_tag
def get_content_type(obj):
    content_type = ContentType.objects.get_for_model(obj)
    return content_type.model