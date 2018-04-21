# ~*~ coding: utf-8 ~*~

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField

from common.utils import validate_ssh_public_key, generate_activation_code
from .models import User, UserGroup
from django.conf import settings
from common.ldapadmin import LDAPTool
from django.contrib import messages


class LDAPUserUpdateForm(forms.Form):
    objectClass = forms.CharField(label=_('objectClass'), max_length=32)
    uid = forms.CharField(label=_('uid'), max_length=32, required=True)
    cn = forms.CharField(label=_('cn'), max_length=32, required=True)
    mail = forms.EmailField(label=_('mail'), required=True)
    givenName = forms.CharField(label=_('givenName'), max_length=32)
    displayName = forms.CharField(label=_('displayName'), max_length=32)
    employeeNumber = forms.CharField(label=_('employeeNumber'), max_length=32)
    mobile = forms.CharField(label=_('mobile'), max_length=32)
    postalAddress = forms.CharField(label=_('postalAddress'), max_length=32)
    # password = forms.CharField(
    #     label=_('Password'), widget=forms.PasswordInput,
    #     max_length=128, strip=False
    # )

    # def __init__(self, *args, **kwargs):
    #     super(LDAPUserUpdateForm, self).__init__(*args, **kwargs)
    #     self.fields['objectClass'].value = "test"


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label=_('Username'), max_length=100)
    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput,
        max_length=128, strip=False
    )
    captcha = CaptchaField()


class UserUpdateForm(forms.ModelForm):
    role_choices = ((i, n) for i, n in User.ROLE_CHOICES if i != User.ROLE_APP)
    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput,
        max_length=128, strip=False, required=False,
    )
    role = forms.ChoiceField(choices=role_choices, required=True, initial=User.ROLE_USER, label=_("Role"))
    public_key = forms.CharField(
        label=_('ssh public key'), max_length=5000, required=False,
        widget=forms.Textarea(attrs={'placeholder': _('ssh-rsa AAAA...')}),
        help_text=_('Paste user id_rsa.pub here.')
    )

    class Meta:
        model = User
        fields = [
            'username', 'is_ldap_user', 'name', 'email', 'groups', 'wechat',
            'phone', 'role', 'date_expired', 'comment',
        ]
        help_texts = {
            'username': '* required',
            'name': '* required',
            'email': '* required',
        }
        widgets = {
            'groups': forms.SelectMultiple(
                attrs={
                    'class': 'select2',
                    'data-placeholder': _('Join user groups')
                }
            ),
        }

    def clean_public_key(self):
        public_key = self.cleaned_data['public_key']
        if not public_key:
            return public_key
        if self.instance.public_key and public_key == self.instance.public_key:
            msg = _('Public key should not be the same as your old one.')
            raise forms.ValidationError(msg)

        if not validate_ssh_public_key(public_key):
            raise forms.ValidationError(_('Not a valid ssh public key'))
        return public_key

    def save(self, commit=True):
        password = self.cleaned_data.get('password')
        public_key = self.cleaned_data.get('public_key')
        user = super().save(commit=commit)

        is_ldap_user = user.is_ldap_user
        # ldap用户
        username = user.username
        if settings.AUTH_LDAP:
            ldap_tool = LDAPTool()
            check_user_code, data = ldap_tool.check_user_status(username)
            if is_ldap_user and check_user_code == 200:
                print("更新用户，类型为ldap")
                old = {'mail': data[1].get('mail', ''), 'mobile': data[1].get('mobile', '')}
                new = {'mail': [user.email.encode('utf-8')], 'mobile': [user.phone.encode('utf-8')],}
                status = ldap_tool.ldap_update_user(username, old, new)
                if status:
                    return user
        # #本地用户
        if password and not is_ldap_user:
            user.set_password(password)
            user.save()
        if public_key:
            user.public_key = public_key
            user.save()
        return user


class UserCreateUpdateForm(forms.ModelForm):
    def __init__(self, request, *args, **kwargs):
        # 如果需要额外接收参数，要重写构造器函数
        # 这里额外接收一个参数，用于从request.sesssion中提取之前保存的验证码
        super().__init__(*args, **kwargs)
        self.request = request

    role_choices = ((i, n) for i, n in User.ROLE_CHOICES if i != User.ROLE_APP)
    password = forms.CharField(
        label=_('Password'), widget=forms.PasswordInput,
        max_length=128, strip=False, required=False,
    )
    role = forms.ChoiceField(choices=role_choices, required=True, initial=User.ROLE_USER, label=_("Role"))
    public_key = forms.CharField(
        label=_('ssh public key'), max_length=5000, required=False,
        widget=forms.Textarea(attrs={'placeholder': _('ssh-rsa AAAA...')}),
        help_text=_('Paste user id_rsa.pub here.')
    )
    is_ldap_user = forms.BooleanField(required=False, label=_("is ldap"))

    class Meta:
        model = User
        fields = [
            'username', 'is_ldap_user', 'name', 'email', 'groups', 'wechat',
            'phone', 'role', 'date_expired', 'comment',
        ]
        help_texts = {
            'username': '* required',
            'name': '* required',
            'email': '* required',
        }
        widgets = {
            'groups': forms.SelectMultiple(
                attrs={
                    'class': 'select2',
                    'data-placeholder': _('Join user groups')
                }
            ),
        }

    def clean_public_key(self):
        public_key = self.cleaned_data['public_key']
        if not public_key:
            return public_key
        if self.instance.public_key and public_key == self.instance.public_key:
            msg = _('Public key should not be the same as your old one.')
            raise forms.ValidationError(msg)

        if not validate_ssh_public_key(public_key):
            raise forms.ValidationError(_('Not a valid ssh public key'))
        return public_key

    def save(self, commit=True):
        password = self.cleaned_data.get('password')
        public_key = self.cleaned_data.get('public_key')
        is_ldap_user = self.cleaned_data.get('is_ldap_user')
        user = super().save(commit=commit)
        # ldap用户
        username = user.username
        if settings.AUTH_LDAP:
            ldap_tool = LDAPTool()
            check_user_code,_ = ldap_tool.check_user_status(username)
            if is_ldap_user and check_user_code == 404:
                print("新增用户，类型为ldap")
                cn = user.username
                mail = user.email
                if password:
                    password = password
                else:
                    password = generate_activation_code(n=1)[0]
                status = ldap_tool.ldap_add_user(cn, mail, username, password)
                if status:
                    msg = "ldap用户创建成功"
                    messages.add_message(self.request, messages.SUCCESS, msg)
                    return user
                else:
                    msg = "ldap用户创建失败"
                    messages.add_message(self.request, messages.ERROR, msg)
        #本地用户
        if password and not is_ldap_user:
            user.set_password(password)
            user.save()
        if public_key:
            user.public_key = public_key
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    def __init__(self, request, *args, **kwargs):
        # 如果需要额外接收参数，要重写构造器函数
        # 这里额外接收一个参数，用于从request.sesssion中提取之前保存的验证码
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.request = request

    class Meta:
        model = User
        fields = [
            'username', 'name', 'email',
            'wechat', 'phone',
        ]
        help_texts = {
            'username': '* required',
            'name': '* required',
            'email': '* required',
        }

    def save(self, commit=True):
        user = super().save(commit=commit)
        #LDAP用户
        if settings.AUTH_LDAP and user.is_ldap_user:
            ldap_tool = LDAPTool()
            check_user_code, data = ldap_tool.check_user_status(user.username)
            if check_user_code == 200:
                print("更新用户，类型为ldap")
                phone = user.phone
                old = {'mail': data[1].get('mail', '')}
                new = {'mail': [user.email.encode('utf-8')], }
                if phone:
                    old = {'mail': data[1].get('mail', ''), 'mobile': data[1].get('mobile', '')}
                    new = {'mail': [user.email.encode('utf-8')], 'mobile': [phone.encode('utf-8')], }
                status = ldap_tool.ldap_update_user(user.username, old, new)

                if not status:
                    msg = "ldap用户更新失败"
                    messages.add_message(self.request, messages.ERROR, msg)
                else:
                    messages.add_message(self.request, messages.INFO, "ldap信息更新成功")
        return user


UserProfileForm.verbose_name = _("Profile")


class UserPasswordForm(forms.Form):
    old_password = forms.CharField(
        max_length=128, widget=forms.PasswordInput,
        label=_("Old password")
    )
    new_password = forms.CharField(
        min_length=5, max_length=128,
        widget=forms.PasswordInput,
        label=_("New password")
    )
    confirm_password = forms.CharField(
        min_length=5, max_length=128,
        widget=forms.PasswordInput,
        label=_("Confirm password")
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if settings.AUTH_LDAP and self.instance.is_ldap_user:
            # 使用LDAP验证时
            ldap_tool = LDAPTool()
            username = self.instance.username
            if ldap_tool.ldap_get_vaild(uid=username, passwd=old_password):
                return old_password
        if not self.instance.check_password(old_password):
            raise forms.ValidationError(_('Old password error'))
        return old_password

    def clean_confirm_password(self):
        new_password = self.cleaned_data['new_password']
        confirm_password = self.cleaned_data['confirm_password']

        if new_password != confirm_password:
            raise forms.ValidationError(_('Password does not match'))
        return confirm_password

    def save(self):
        username = self.instance.username
        password = self.cleaned_data['new_password']
        self.instance.set_password(password)
        self.instance.save()
        # ldap用户
        if settings.AUTH_LDAP and self.instance.is_ldap_user:
            ldap_tool = LDAPTool()
            status = ldap_tool.ldap_update_password(username, new_password=password)
            if status:
                return self.instance
        return self.instance


class UserPublicKeyForm(forms.Form):
    public_key = forms.CharField(
        label=_('ssh public key'), max_length=5000, required=False,
        widget=forms.Textarea(attrs={'placeholder': _('ssh-rsa AAAA...')}),
        help_text=_('Paste your id_rsa.pub here.')
    )

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            self.instance = kwargs.pop('instance')
        else:
            self.instance = None
        super().__init__(*args, **kwargs)

    def clean_public_key(self):
        public_key = self.cleaned_data['public_key']
        if self.instance.public_key and public_key == self.instance.public_key:
            msg = _('Public key should not be the same as your old one.')
            raise forms.ValidationError(msg)

        if public_key and not validate_ssh_public_key(public_key):
            raise forms.ValidationError(_('Not a valid ssh public key'))
        return public_key

    def save(self):
        public_key = self.cleaned_data['public_key']
        if public_key:
            self.instance.public_key = public_key
            self.instance.save()
        return self.instance


UserPublicKeyForm.verbose_name = _("Public key")


class UserBulkUpdateForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        required=True,
        help_text='* required',
        label=_('Select users'),
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select users')
            }
        )
    )

    class Meta:
        model = User
        fields = ['users', 'role', 'groups', 'date_expired']
        widgets = {
            "groups": forms.SelectMultiple(
                attrs={
                    'class': 'select2',
                    'data-placeholder': _('Select users')
                }
            )
        }

    def save(self, commit=True):
        changed_fields = []
        for field in self._meta.fields:
            if self.data.get(field) is not None:
                changed_fields.append(field)

        cleaned_data = {k: v for k, v in self.cleaned_data.items()
                        if k in changed_fields}
        users = cleaned_data.pop('users', '')
        groups = cleaned_data.pop('groups', [])
        users = User.objects.filter(id__in=[user.id for user in users])
        users.update(**cleaned_data)
        if groups:
            for user in users:
                user.groups.set(groups)
        return users


class UserGroupForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.exclude(role=User.ROLE_APP),
        label=_("User"),
        widget=forms.SelectMultiple(
            attrs={
                'class': 'select2',
                'data-placeholder': _('Select users')
            }
        ),
        required=False,
    )

    def __init__(self, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            initial.update({
                'users': instance.users.all(),
            })
            kwargs['initial'] = initial
        super().__init__(**kwargs)

    def save(self, commit=True):
        group = super().save(commit=commit)
        users = self.cleaned_data['users']
        group.users.set(users)
        return group

    class Meta:
        model = UserGroup
        fields = [
            'name', 'users', 'comment'
        ]
        help_texts = {
            'name': '* required'
        }


#class UserGroupPrivateAssetPermissionForm(forms.ModelForm):
#    def save(self, commit=True):
#        self.instance = super(UserGroupPrivateAssetPermissionForm, self)\
#            .save(commit=commit)
#        self.instance.user_groups = [self.user_group]
#        self.instance.save()
#        return self.instance
#
#    class Meta:
#        model = AssetPermission
#        fields = [
#            'assets', 'asset_groups', 'system_users', 'name',
#        ]
#        widgets = {
#            'assets': forms.SelectMultiple(
#                attrs={'class': 'select2',
#                       'data-placeholder': _('Select assets')}),
#            'asset_groups': forms.SelectMultiple(
#                attrs={'class': 'select2',
#                       'data-placeholder': _('Select asset groups')}),
#            'system_users': forms.SelectMultiple(
#                attrs={'class': 'select2',
#                       'data-placeholder': _('Select system users')}),
#        }
#

class FileForm(forms.Form):
    file = forms.FileField()
