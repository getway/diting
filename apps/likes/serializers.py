# -*- coding: utf-8 -*-
#
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_bulk import BulkListSerializer
from common.mixins import BulkSerializerMixin
from .models import LikeRecord, LikeCount, ViewCount, ViewRecord
from rest_framework import generics
from users.models import User


class ViewCountSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ViewCount
        list_serializer_class = BulkListSerializer
        fields = '__all__'

    def get_field_names(self, declared_fields, info):
        fields = super(ViewCountSerializer, self).get_field_names(declared_fields, info)
        return fields


class ViewCountUpdateNumSerializer(serializers.ModelSerializer):
    class Meta:
        model = ViewCount
        fields = ['id', 'num']


class ViewRecordSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ViewRecord
        list_serializer_class = BulkListSerializer
        fields = '__all__'

    def get_field_names(self, declared_fields, info):
        fields = super(ViewRecordSerializer, self).get_field_names(declared_fields, info)
        return fields


class LikeCountSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = LikeCount
        list_serializer_class = BulkListSerializer
        fields = '__all__'

    def get_field_names(self, declared_fields, info):
        fields = super(LikeCountSerializer, self).get_field_names(declared_fields, info)
        return fields


class LikeCountUpdateNumSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikeCount
        fields = ['id', 'liked_num']


class LikeRecordSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = LikeRecord
        list_serializer_class = BulkListSerializer
        fields = '__all__'

    def get_field_names(self, declared_fields, info):
        fields = super(LikeRecordSerializer, self).get_field_names(declared_fields, info)
        return fields

