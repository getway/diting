#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/6 下午5:13
# @Author  : xiaomao
# @Site    : 
# @File    : api.py
# @Software: PyCharm

from .models import Projects
from . import serializers
from common.utils import get_logger
from .hands import IsSuperUser, IsSuperUserOrAppUser
from rest_framework_bulk import BulkModelViewSet
from rest_framework import generics


class ProjectsViewSet(BulkModelViewSet):
    """
    Projects api set, for add,delete,update,list,retrieve resource
    """
    queryset = Projects.objects.all()
    serializer_class = serializers.ProjectsSerializer
    permission_classes = (IsSuperUserOrAppUser,)

class ProjectsUpdateGroupApi(generics.RetrieveUpdateAPIView):
    queryset = Projects.objects.all()
    serializer_class = serializers.ProjectsUpdateGroupSerializer
    permission_classes = (IsSuperUser,)

class ProjectsUpdateUserApi(generics.RetrieveUpdateAPIView):
    queryset = Projects.objects.all()
    serializer_class = serializers.ProjectsUpdateUserSerializer
    permission_classes = (IsSuperUser,)