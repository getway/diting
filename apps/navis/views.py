#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/6 下午4:01
# @Author  : xiaomao
# @Site    : 
# @File    : views.py
# @Software: PyCharm

from users.models import User, UserGroup
from .models import Navi
from common.utils import get_logger, get_object_or_none, is_uuid, ssh_key_gen
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import (
    CreateView, UpdateView
)
from django.views.generic.detail import DetailView, SingleObjectMixin
from .utils import AdminUserRequiredMixin
from . import forms
from common.const import create_success_msg, update_success_msg

logger = get_logger(__name__)


class NaviListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'navis/navi_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Navis'),
            'action': _('Navi'),
        })
        return context


class NaviCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Navi
    form_class = forms.NaviCreateUpdateForm
    template_name = 'navis/navi_create_update.html'
    success_url = reverse_lazy('navis:navi-list')
    success_message = create_success_msg

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'app': _('Navis'), 'action': _('Create Navi')})
        return context

    def form_valid(self, form):
        navi = form.save(commit=False)
        navi.created_by = self.request.user.username or 'System'
        navi.save()
        return super().form_valid(form)


class NaviUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Navi
    form_class = forms.NaviUpdateForm
    template_name = 'navis/navi_create_update.html'
    context_object_name = 'navi_object'
    success_url = reverse_lazy('navis:navi-list')
    success_message = update_success_msg

    def get_context_data(self, **kwargs):
        context = {'app': _('Navis'), 'action': _('Update navi')}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class NaviDetailView(AdminUserRequiredMixin, DetailView):
    model = Navi
    template_name = 'navis/navi_detail.html'
    context_object_name = "navi_object"

    def get_context_data(self, **kwargs):
        groups = UserGroup.objects.exclude(id__in=self.object.groups.all())
        users = User.objects.exclude(id__in=self.object.users.all())
        context = {
            'app': _('Navis'),
            'action': _('Navi detail'),
            'groups': groups,
            'users': users,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)