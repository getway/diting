# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals


from django.conf.urls import url
from .. import views

__all__ = ["urlpatterns"]

app_name = "projects"

urlpatterns = [
    # TResource projects url
    url(r'^projects/$', views.ProjectsListView.as_view(), name='projects-list'),
    url(r'^projects/create/$', views.ProjectsCreateView.as_view(), name='projects-create'),
    url(r'^projects/(?P<pk>[0-9a-zA-Z\-]{36})/update$', views.ProjectsUpdateView.as_view(), name='projects-update'),
    url(r'^projects/(?P<pk>[0-9a-zA-Z\-]{36})$', views.ProjectsDetailView.as_view(), name='projects-detail'),
]
