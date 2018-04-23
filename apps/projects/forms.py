#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/6 下午3:58
# @Author  : xiaomao
# @Site    : 
# @File    : forms.py
# @Software: PyCharm


from django import forms
from .models import Projects


class ProjectsCreateUpdateForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ProjectsCreateUpdateForm, self).clean()
        value = cleaned_data.get('name')
        try:
            Projects.objects.get(name=value)
            self._errors['name']=self.error_class(["%s的信息已经存在" % value])
        except Projects.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = Projects
        exclude = ("id",)


class ProjectsUpdateForm(forms.ModelForm):
    class Meta:
        model = Projects
        exclude = ("id",)
