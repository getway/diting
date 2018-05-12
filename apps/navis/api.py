#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/6 下午5:13
# @Author  : xiaomao
# @Site    : 
# @File    : api.py
# @Software: PyCharm

from .models import Navi
from . import serializers
from common.utils import get_logger
from .hands import IsSuperUser, IsSuperUserOrAppUser
from rest_framework_bulk import BulkModelViewSet
from rest_framework import generics


class NaviViewSet(BulkModelViewSet):
    """
    Navi api set, for add,delete,update,list,retrieve resource
    """
    queryset = Navi.objects.all()
    serializer_class = serializers.NaviSerializer
    permission_classes = (IsSuperUserOrAppUser,)


class NaviUpdateGroupApi(generics.RetrieveUpdateAPIView):
    queryset = Navi.objects.all()
    serializer_class = serializers.NaviUpdateGroupSerializer
    permission_classes = (IsSuperUser,)

class NaviUpdateUserApi(generics.RetrieveUpdateAPIView):
    queryset = Navi.objects.all()
    serializer_class = serializers.NaviUpdateUserSerializer
    permission_classes = (IsSuperUser,)