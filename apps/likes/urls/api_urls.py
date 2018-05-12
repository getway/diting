# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .. import api

app_name = "likes"

router = DefaultRouter()
router.register(r'v1/like-count', api.LikeCountViewSet, 'like-count')
router.register(r'v1/like-record', api.LikeRecordViewSet, 'like-record')
router.register(r'v1/view-count', api.ViewCountViewSet, 'view-count')
router.register(r'v1/view-record', api.ViewRecordViewSet, 'view-record')

urlpatterns = [
    url(r'^like-change$', api.LikeChange.as_view(), name='like-change'),
]

urlpatterns += router.urls