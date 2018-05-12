#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/6 下午5:13
# @Author  : xiaomao
# @Site    : 
# @File    : api.py
# @Software: PyCharm

from . import serializers
from rest_framework_bulk import BulkModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import ObjectDoesNotExist
from .models import LikeCount, LikeRecord, ViewRecord, ViewCount


def ErrorResponse(code, message):
    data = {}
    data['status'] = 'ERROR'
    data['code'] = code
    data['message'] = message
    return JsonResponse(data)


def SuccessResponse(liked_num):
    data = {}
    data['status'] = 'SUCCESS'
    data['liked_num'] = liked_num
    return JsonResponse(data)


class LikeChange(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        content_type = request.GET.get('content_type')
        object_id = request.GET.get('object_id')

        try:
            content_type = ContentType.objects.get(model=content_type)

            model_class = content_type.model_class()
            model_obj = model_class.objects.get(pk=object_id)
            # print(content_type, model_class, model_obj)
        except Exception as e:
            print(e)
            return ErrorResponse(404, 'object not exist')

        # 处理数据
        if request.GET.get('is_like') == 'true':
            # 要点赞
            like_record, created = LikeRecord.objects.get_or_create(content_type=content_type, object_id=object_id,
                                                                    user=user)
            if created:
                # 未点赞过，进行点赞
                like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
                like_count.liked_num += 1
                like_count.save()
                return SuccessResponse(like_count.liked_num)
            else:
                # 已点赞过，不能重复点赞
                return ErrorResponse(402, 'you were liked')
        else:
            # 要取消点赞
            if LikeRecord.objects.filter(content_type=content_type, object_id=object_id, user=user).exists():
                # 有点赞过，取消点赞
                like_record = LikeRecord.objects.get(content_type=content_type, object_id=object_id, user=user)
                like_record.delete()
                # 点赞总数减1
                like_count, created = LikeCount.objects.get_or_create(content_type=content_type, object_id=object_id)
                if not created:
                    like_count.liked_num -= 1
                    like_count.save()
                    return SuccessResponse(like_count.liked_num)
                else:
                    return ErrorResponse(404, 'data error')
            else:
                # 没有点赞过，不能取消
                return ErrorResponse(403, 'you were not liked')


class ViewCountViewSet(BulkModelViewSet):
    """
    ViewCount api set, for add,delete,update,list,retrieve resource
    """
    queryset = ViewCount.objects.all()
    serializer_class = serializers.ViewCountSerializer
    permission_classes = (IsAuthenticated,)


class ViewRecordViewSet(BulkModelViewSet):
    """
    ViewRecord api set, for add,delete,update,list,retrieve resource
    """
    queryset = ViewRecord.objects.all()
    serializer_class = serializers.ViewRecordSerializer
    permission_classes = (IsAuthenticated,)


class LikeCountViewSet(BulkModelViewSet):
    """
    LikeCount api set, for add,delete,update,list,retrieve resource
    """
    queryset = LikeCount.objects.all()
    serializer_class = serializers.LikeCountSerializer
    permission_classes = (IsAuthenticated,)


class LikeRecordViewSet(BulkModelViewSet):
    """
    LikeRecord api set, for add,delete,update,list,retrieve resource
    """
    queryset = LikeRecord.objects.all()
    serializer_class = serializers.LikeRecordSerializer
    permission_classes = (IsAuthenticated,)
