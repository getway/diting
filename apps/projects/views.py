#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/6 下午4:01
# @Author  : xiaomao
# @Site    : 
# @File    : views.py
# @Software: PyCharm

from apps.users.models import User, UserGroup
from .models import Navi
from django.shortcuts import render
from .forms import NaviCreateUpdateForm
from django.contrib.auth.decorators import login_required
from apps.common.utils import get_logger, get_object_or_none, is_uuid, ssh_key_gen
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import TemplateView
from django.db import transaction
from django.views.generic.edit import (
    CreateView, UpdateView, FormMixin, FormView
)
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout as auth_logout
from .utils import AdminUserRequiredMixin
from . import forms
from apps.common.const import create_success_msg, update_success_msg

logger = get_logger(__name__)


class ProjectsListView(AdminUserRequiredMixin, TemplateView):
    template_name = 'projects/projects_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Projects'),
            'action': _('Projects'),
        })
        return context


class ProjectsCreateView(AdminUserRequiredMixin, SuccessMessageMixin, CreateView):
    model = Navi
    form_class = forms.NaviCreateUpdateForm
    template_name = 'projects/projects_create_update.html'
    success_url = reverse_lazy('projects:projects-list')
    success_message = create_success_msg

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'app': _('Projects'), 'action': _('Create Projects')})
        return context

    def form_valid(self, form):
        navi = form.save(commit=False)
        navi.created_by = self.request.user.username or 'System'
        navi.save()
        return super().form_valid(form)


class ProjectsUpdateView(AdminUserRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Navi
    form_class = forms.NaviUpdateForm
    template_name = 'projects/Projects_create_update.html'
    context_object_name = 'projects_object'
    success_url = reverse_lazy('projects:projects-list')
    success_message = update_success_msg

    def get_context_data(self, **kwargs):
        context = {'app': _('Projects'), 'action': _('Update projects')}
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class ProjectsDetailView(AdminUserRequiredMixin, DetailView):
    model = Navi
    template_name = 'projects/projects_detail.html'
    context_object_name = "projects_object"

    def get_context_data(self, **kwargs):
        groups = UserGroup.objects.exclude(id__in=self.object.groups.all())
        users = User.objects.exclude(id__in=self.object.users.all())
        context = {
            'app': _('Projects'),
            'action': _('Projects detail'),
            'groups': groups,
            'users': users,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)