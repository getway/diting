import datetime

from django.http import HttpResponse
from django.views.generic import TemplateView, View
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from users.models import User
from navis.models import Navi

from common.utils import get_object_or_none
from django.utils.http import urlquote
import json
from likes.utils import set_view_count


class UrlView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        user = request.user
        #获取客户端传来的参数PK
        pk = kwargs.get('pk')
        navi = get_object_or_none(Navi, name=pk)
        access_code, access_msg = 0, ''
        try:
            if navi:
                is_user = navi.users.filter(name=user.name)
                #获取所有用户组里的用户列表
                groups_users = [user.name for group in navi.groups.all() for user in group.users.all()]
                url = navi.url
                from django.core.cache import cache
                if is_user or user.name in groups_users:
                    #有权限
                    access_code = 200
                    access_msg = "正常访问"
                    return redirect(url)
                else:
                    #没有权限
                    access_code = 403
                    access_msg = "没有权限"
                    return HttpResponse(status=access_code)
            else:
                #没有此navi
                access_code = 404
                access_msg = "没有此导航"
                return HttpResponse(status=access_code)
        except Exception as e:
            #访问过程错误
            print(e)
            access_code = 500
            access_msg = e
            return HttpResponse(status=access_code)
        finally:
            set_view_count(user.username, 'navi', navi.id, access_status=access_code, access_message=access_msg)


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