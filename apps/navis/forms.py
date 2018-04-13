#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/6 下午3:58
# @Author  : xiaomao
# @Site    : 
# @File    : forms.py
# @Software: PyCharm


from django import forms
from .models import Navi


class NaviCreateUpdateForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(NaviCreateUpdateForm, self).clean()
        value = cleaned_data.get('name')
        try:
            Navi.objects.get(name=value)
            self._errors['name']=self.error_class(["%s的信息已经存在" % value])
        except Navi.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = Navi
        exclude = ("id",)


class NaviUpdateForm(forms.ModelForm):
    class Meta:
        model = Navi
        exclude = ("id",)
