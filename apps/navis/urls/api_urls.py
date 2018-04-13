# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from .. import api


app_name = "navi"

router = DefaultRouter()
router.register(r'v1/navi', api.NaviViewSet, 'navi')

urlpatterns = [
        url(r'^v1/navis/(?P<pk>[0-9a-zA-Z\-]{36})/groups/$',
                api.NaviUpdateGroupApi.as_view(), name='navi-update-group'),
        url(r'^v1/navis/(?P<pk>[0-9a-zA-Z\-]{36})/users/$',
                api.NaviUpdateUserApi.as_view(), name='navi-update-user'),
]

urlpatterns += router.urls