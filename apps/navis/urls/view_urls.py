# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals


from django.conf.urls import url
from .. import views

__all__ = ["urlpatterns"]

app_name = "navi"

urlpatterns = [
    # TResource Navi url
    url(r'^navi/$', views.NaviListView.as_view(), name='navi-list'),
    url(r'^navi/create/$', views.NaviCreateView.as_view(), name='navi-create'),
    url(r'^navi/(?P<pk>[0-9a-zA-Z\-]{36})/update$', views.NaviUpdateView.as_view(), name='navi-update'),
    url(r'^navi/(?P<pk>[0-9a-zA-Z\-]{36})$', views.NaviDetailView.as_view(), name='navi-detail'),
]
