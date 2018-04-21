# ~*~ coding: utf-8 ~*~

from __future__ import absolute_import, unicode_literals
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import NaviPermission

class NaviPermissionForm(forms.ModelForm):
    class Meta:
        model = NaviPermission
        fields = [
            'navi', 'users', 'user_groups',
            'date_expired', 'comment',
        ]
        widgets = {
            'node': forms.Select(
                attrs={'style': 'display:none'}
            ),
            'user_group': forms.Select(
                attrs={'class': 'select2', 'data-placeholder': _("User group")}
            ),
            'system_user': forms.Select(
                attrs={'class': 'select2', 'data-placeholder': _('System user')}
            ),
        }

    def clean_system_user(self):
        return self.cleaned_data['system_user']
