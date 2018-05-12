# -*- coding: utf-8 -*-
#
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_bulk import BulkListSerializer
from common.mixins import BulkSerializerMixin
from .models import Navi
from rest_framework import generics
from users.models import User, UserGroup


class NaviSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Navi
        list_serializer_class = BulkListSerializer
        fields = '__all__'
        # exclude = ['id']

    def get_field_names(self, declared_fields, info):
        fields = super(NaviSerializer, self).get_field_names(declared_fields, info)
        return fields


class NaviPKUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navi
        fields = ['id', 'logo']


class NaviUpdateGroupSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=UserGroup.objects.all())

    class Meta:
        model = Navi
        fields = ['id', 'groups']


class NaviUpdateUserSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Navi
        fields = ['id', 'users']