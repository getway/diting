# ~*~ coding: utf-8 ~*~

from __future__ import unicode_literals, absolute_import

from django.utils.translation import ugettext as _
from django.views.generic import ListView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from common.utils import get_object_or_none
from .hands import AdminUserRequiredMixin


