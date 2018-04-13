from __future__ import unicode_literals

from django.apps import AppConfig


class NaviConfig(AppConfig):
    name = 'navis'

    def ready(self):
        from . import signals_handler
        return super().ready()