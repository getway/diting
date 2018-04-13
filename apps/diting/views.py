import datetime

from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from users.models import User
from navis.models import Navi


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    session_week = None
    session_month = None
    session_month_dates = []
    session_month_dates_archive = []

    def get(self, request, *args, **kwargs):
        return super(IndexView, self).get(request, *args, **kwargs)

    @staticmethod
    def get_user_count():
        return User.objects.filter(role__in=('Admin', 'User')).count()

    def get_context_data(self, **kwargs):
        navis = Navi.objects.all()
        context = {
            'users_count': self.get_user_count(),
            'navis': navis,
        }
        kwargs.update(context)
        return super(IndexView, self).get_context_data(**kwargs)