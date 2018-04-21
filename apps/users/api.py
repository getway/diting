# ~*~ coding: utf-8 ~*~
import uuid
from django.core.cache import cache
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_bulk import BulkModelViewSet

from .serializers import UserSerializer, UserGroupSerializer, \
    UserGroupUpdateMemeberSerializer, UserPKUpdateSerializer, \
    UserUpdateGroupSerializer, ChangeUserPasswordSerializer
from .tasks import write_login_log_async
from .models import User, UserGroup
from .permissions import IsSuperUser, IsValidUser, IsCurrentUserOrReadOnly, \
    IsSuperUserOrAppUser
from .utils import check_user_valid, generate_token
from common.mixins import IDInFilterMixin
from common.utils import get_logger
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from ldap3 import Server, Connection
from django.conf import settings
from common.ldapadmin import LDAPTool


logger = get_logger(__name__)


class LDAPUserDetailAPI(APIView):
    """
    LDAP用户属性
    """
    permission_classes = (IsSuperUser,)
    success_message = _("ldap user search success")

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        data = {'status': '', 'msg': '', 'data': ''}
        if settings.AUTH_LDAP:
            try:
                ldap_tool = LDAPTool()
                status = ldap_tool.ldap_get_user(pk, isdict=True)
                if status:
                    data['msg'] = "用户:%s 获取成功" % pk
                    data['data'] = status
                    data['status'] = 200
                else:
                    data['msg'] = "未获取用户:%s" % pk
                    data['status'] = 404
                return Response(data=data, status=200)
            except Exception as e:
                data['msg'] = "用户:%s 获取失败，原因:%s" % (pk, str(e))
                data['status'] = 500
                return Response(data=data, status=200)
        else:
            data['msg'] = '请系统先支持ldap'
            data['status'] = 501
            return Response(data=data, status=200)

    def delete(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        data = {'status': '', 'msg': ''}
        if settings.AUTH_LDAP:
            try:
                ldap_tool = LDAPTool()
                status = ldap_tool.ldap_delete(pk)
                user = User.objects.filter(username=pk)
                if user:
                    #如果该用户是系统用户，删除ldap时候，顺便把系统中用户也删除了
                    user.delete()
                if status:
                    msg = "用户:%s 删除成功" % pk
                    rt = 200
                else:
                    msg = "用户%s 删除失败" % pk
                    rt = 511
                data['msg'] = msg
                data['status'] = rt
            except Exception as e:
                msg = str(e)
                rt = 500
                data['msg'] = msg
                data['status'] = rt
                return Response(data=data, status=data['status'])
            return Response(data=data, status=data['status'])
        else:
            data['msg'] = '请系统先支持ldap'
            data['status'] = 512
            return Response(data=data, status=data['status'])


class LDAPUserListAPI(APIView):
    """
    列出所有LDAP用户
    """
    permission_classes = (IsSuperUser,)
    success_message = _("ldap user search success")

    def get(self, request):
        host = settings.AUTH_LDAP_SERVER_URI
        bind_dn = settings.AUTH_LDAP_BIND_DN
        password = settings.AUTH_LDAP_BIND_PASSWORD
        use_ssl = settings.AUTH_LDAP_START_TLS
        search_ou = settings.AUTH_LDAP_SEARCH_OU
        search_filter = settings.AUTH_LDAP_SEARCH_FILTER
        attr_map = settings.AUTH_LDAP_USER_ATTR_MAP

        server = Server(host, use_ssl=use_ssl)
        conn = Connection(server, bind_dn, password)
        try:
            conn.bind()
        except Exception as e:
            return Response({"error": str(e)}, status=401)

        ok = conn.search(search_ou, search_filter % ({"user": "*"}),
                         attributes=list(attr_map.values()))
        if not ok:
            return Response({"error": "Search no entry matched"}, status=401)

        users = []
        for entry in conn.entries:
            # user = entry.entry_to_json(include_empty=True)
            # user_dict = json.loads(user)
            user = {}
            for attr, mapping in attr_map.items():
                if hasattr(entry, mapping):
                    user[attr] = getattr(entry, mapping).value

            #判断当前是否导入
            local_user = User.objects.filter(username=user['username'])
            user['id'] = user['username']
            if local_user:
                user['isImported'] = True
                # print("该用户已导入:%s" % local_user[0].username)
            else:
                user['isImported'] = False
                # print("没有导入ldap_local:%s"%local_user)
            users.append(user)
        return Response(data=users, status=200)


class UserViewSet(IDInFilterMixin, BulkModelViewSet):
    queryset = User.objects.exclude(role="App")
    # queryset = User.objects.all().exclude(role="App").order_by("date_joined")
    serializer_class = UserSerializer
    permission_classes = (IsSuperUserOrAppUser, IsAuthenticated)
    filter_fields = ('username', 'email', 'name', 'id')


class ChangeUserPasswordApi(generics.RetrieveUpdateAPIView):
    permission_classes = (IsSuperUser,)
    queryset = User.objects.all()
    serializer_class = ChangeUserPasswordSerializer

    def perform_update(self, serializer):
        user = self.get_object()
        user.password_raw = serializer.validated_data["password"]
        user.save()


class UserUpdateGroupApi(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateGroupSerializer
    permission_classes = (IsSuperUser,)


class UserResetPasswordApi(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def perform_update(self, serializer):
        # Note: we are not updating the user object here.
        # We just do the reset-password stuff.
        import uuid
        from .utils import send_reset_password_mail
        user = self.get_object()
        user.password_raw = str(uuid.uuid4())
        user.save()
        send_reset_password_mail(user)


class UserResetPKApi(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_update(self, serializer):
        from .utils import send_reset_ssh_key_mail
        user = self.get_object()
        user.is_public_key_valid = False
        user.save()
        send_reset_ssh_key_mail(user)


class UserUpdatePKApi(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPKUpdateSerializer
    permission_classes = (IsCurrentUserOrReadOnly,)

    def perform_update(self, serializer):
        user = self.get_object()
        user.public_key = serializer.validated_data['_public_key']
        user.save()


class UserGroupViewSet(IDInFilterMixin, BulkModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer


class UserGroupUpdateUserApi(generics.RetrieveUpdateAPIView):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupUpdateMemeberSerializer
    permission_classes = (IsSuperUser,)


class UserToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        if not request.user.is_authenticated:
            username = request.data.get('username', '')
            email = request.data.get('email', '')
            password = request.data.get('password', '')
            public_key = request.data.get('public_key', '')

            user, msg = check_user_valid(
                username=username, email=email,
                password=password, public_key=public_key)
        else:
            user = request.user
            msg = None
        if user:
            token = generate_token(request, user)
            return Response({'Token': token, 'Keyword': 'Bearer'}, status=200)
        else:
            return Response({'error': msg}, status=406)


class UserProfile(APIView):
    permission_classes = (IsValidUser,)

    def get(self, request):
        return Response(request.user.to_json())

    def post(self, request):
        return Response(request.user.to_json())


class UserAuthApi(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        public_key = request.data.get('public_key', '')
        login_type = request.data.get('login_type', '')
        login_ip = request.data.get('remote_addr', None)
        user_agent = request.data.get('HTTP_USER_AGENT', '')

        if not login_ip:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')

            if x_forwarded_for and x_forwarded_for[0]:
                login_ip = x_forwarded_for[0]
            else:
                login_ip = request.META.get("REMOTE_ADDR")

        user, msg = check_user_valid(
            username=username, password=password,
            public_key=public_key
        )

        if user:
            token = generate_token(request, user)
            write_login_log_async(
                user.username, ip=login_ip,
                type=login_type, user_agent=user_agent,
            )
            # write_login_log_async.delay(
            #     user.username, ip=login_ip,
            #     type=login_type, user_agent=user_agent,
            # )
            return Response({'token': token, 'user': user.to_json()})
        else:
            return Response({'msg': msg}, status=401)


class UserConnectionTokenApi(APIView):
    permission_classes = (IsSuperUserOrAppUser,)

    def post(self, request):
        user_id = request.data.get('user', '')
        asset_id = request.data.get('asset', '')
        system_user_id = request.data.get('system_user', '')
        token = str(uuid.uuid4())
        value = {
            'user': user_id,
            'asset': asset_id,
            'system_user': system_user_id
        }
        cache.set(token, value, timeout=20)
        return Response({"token": token}, status=201)

    def get(self, request):
        token = request.query_params.get('token')
        user_only = request.query_params.get('user-only', None)
        value = cache.get(token, None)

        if not value:
            return Response('', status=404)

        if not user_only:
            return Response(value)
        else:
            return Response({'user': value['user']})

    def get_permissions(self):
        if self.request.query_params.get('user-only', None):
            self.permission_classes = (AllowAny,)
        return super().get_permissions()
