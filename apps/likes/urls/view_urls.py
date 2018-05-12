# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals


from django.conf.urls import url
from .. import views

__all__ = ["urlpatterns"]

app_name = "likes"

urlpatterns = [
    # TResource Likes url
    # url(r'^likes/$', views.LikeChange.as_view(), name='like-change'),
]
