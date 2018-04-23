# -*- coding: utf-8 -*-
#
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_bulk import BulkListSerializer
from apps.common.mixins import BulkSerializerMixin
from .models import Projects
from rest_framework import generics
from apps.users.models import User, UserGroup


class ProjectsSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Projects
        list_serializer_class = BulkListSerializer
        fields = '__all__'
        # exclude = ['id']

    def get_field_names(self, declared_fields, info):
        fields = super(ProjectsSerializer, self).get_field_names(declared_fields, info)
        return fields

class ProjectsPKUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'dever']


class ProjectsUpdateGroupSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=UserGroup.objects.all())

    class Meta:
        model = Projects
        fields = ['id', 'groups']


class ProjectsUpdateUserSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Projects
        fields = ['id', 'users']