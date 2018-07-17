# ~*~ coding: utf-8 ~*~
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

from .views import IndexView, UrlView

schema_view = get_schema_view(title='Users API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^url/(?P<pk>.+)$', UrlView.as_view(), name='url-redirect'),
    url(r'^users/', include('users.urls.views_urls', namespace='users')),
    url(r'^perms/', include('perms.urls.views_urls', namespace='perms')),
    url(r'^settings/', include('common.urls.view_urls', namespace='settings')),
    url(r'^common/', include('common.urls.view_urls', namespace='common')),
    url(r'^navis/', include('navis.urls.view_urls', namespace='navis')),
    url(r'^likes/', include('likes.urls.view_urls', namespace='likes')),

    # Api url view map
    url(r'^api/users/', include('users.urls.api_urls', namespace='api-users')),
    url(r'^api/common/', include('common.urls.api_urls', namespace='api-common')),
    url(r'^api/navis/', include('navis.urls.api_urls', namespace='api-navis')),
    url(r'^api/likes/', include('likes.urls.api_urls', namespace='api-likes')),

    # External apps url
    url(r'^captcha/', include('captcha.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^docs/', schema_view, name="docs"),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
      + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
