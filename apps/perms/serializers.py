# -*- coding: utf-8 -*-
#

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from common.utils import get_object_or_none
from common.fields import StringIDField
from .models import NaviPermission


class NaviPermissionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NaviPermission
        fields = [
            'id', 'navi', 'user_group', 'user', 'date_expired'
        ]


class NaviPermissionListSerializer(serializers.ModelSerializer):
    navi = StringIDField(read_only=True)
    user_group = StringIDField(read_only=True)
    user = StringIDField(read_only=True)

    class Meta:
        model = NaviPermission
        fields = '__all__'


class NaviPermissionUpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = NaviPermission
        fields = ['id', 'users']


class NaviPermissionUpdateGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = NaviPermission
        fields = ['id', 'user-groups']


class UserNaviPermissionCreateUpdateSerializer(NaviPermissionCreateUpdateSerializer):
    is_inherited = serializers.SerializerMethodField()

    @staticmethod
    def get_is_inherited(obj):
        if getattr(obj, 'inherited', ''):
            return True
        else:
            return False

