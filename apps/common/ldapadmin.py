#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/15 下午12:37
# @Author  : xiaomao
# @Site    : 
# @File    : ldapadmin.py
# @Software: PyCharm

import ldap
import ldap.modlist as modlist
import logging
from django.conf import settings
from passlib.hash import ldap_salted_sha1 as ssha


logger = logging.getLogger()

# 登陆 地址
LDAP_URI = settings.AUTH_LDAP_SERVER_URI
# 登陆 账户
LDAP_USER = settings.AUTH_LDAP_BIND_DN
# 登陆 密码
LDAP_PASS = settings.AUTH_LDAP_BIND_PASSWORD
# 默认 区域
BASE_DN = settings.AUTH_LDAP_SEARCH_OU


def pass_encrypt(passwd):
    return ssha.encrypt(passwd, salt_size=16)


class LDAPTool(object):
    def __init__(self,
                 ldap_uri=None,
                 base_dn=None,
                 user=None,
                 password=None):
        """
        初始化
        :param ldap_uri: ldap_uri
        :param base_dn: 区域
        :param user: 默认用户
        :param password: 默认密码
        :return:
        """
        if not ldap_uri:
            ldap_uri = LDAP_URI
        if not base_dn:
            self.base_dn = BASE_DN
        if not user:
            self.admin_user = LDAP_USER
        if not password:
            self.admin_password = LDAP_PASS
        try:
            self.ldapconn = ldap.initialize(ldap_uri)  # 老版本使用open方法
            self.ldapconn.simple_bind(self.admin_user, self.admin_password)  # 绑定用户名、密码
        except ldap.LDAPError as e:
            logger.error('ldap conn失败，原因为: %s' % str(e))

    def ldap_search_dn(self, value=None, value_type='uid'):
        """
        # 根据表单提交的用户名，检索该用户的dn,一条dn就相当于数据库里的一条记录。
        # 在ldap里类似cn=username,ou=users,dc=gccmx,dc=cn,验证用户密码，必须先检索出该DN
        :param value: 用户 uid或 组cn
        :param value_type: 用户 uid|cn
        :return: search result
        """
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        if value_type == 'cn':
            searchFilter = "cn=" + value
        else:
            searchFilter = "uid=" + value
        try:
            ldap_result_id = obj.search(
                base=self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                return result_data
            else:
                return None
        except ldap.LDAPError as e:
            logger.error('ldap search %s 失败，原因为: %s' % (value, str(e)))

    def ldap_get_user(self, uid=None):
        """
        通过查询用户uid，从ldap_search_dn进一步提取所需数据，search到的是全部信息
        :param uid:
        :return: {‘uid’:'zhangsan','mail':'zhangsan@xxx.com','cn':'张三'}
        """
        result = None
        try:
            search = self.ldap_search_dn(value=uid, value_type="uid")
            if search is None:
                raise ldap.LDAPError('未查询到相应 id')
            for user in search:
                u = user[1]['uid'][0].decode("utf-8")
                if u == uid:
                    # result = {
                    #     'uid': uid,
                    #     'mail': user[1]['mail'][0].decode("utf-8"),
                    #     'cn': user[1]['cn'][0].decode("utf-8"),
                    # }
                    return user
        except Exception as e:
            logger.error('获取用户%s 失败，原因为: %s' % (uid, str(e)))
        return result

    def __ldap_getgid(self, cn="员工"):
        """
        查询 组cn对应的gid
        :param cn: 组cn
        :return: 对应cn的gidNumber
        """
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = None
        searchFilter = "cn=" + cn
        try:
            ldap_result_id = obj.search(
                base="%s" % self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            result_type, result_data = obj.result(ldap_result_id, 0)
            if result_type == ldap.RES_SEARCH_ENTRY:
                return result_data[0][1].get('gidNumber')[0]
            else:
                return None
        except ldap.LDAPError as e:
            logger.error('获取gid失败，原因为: %s' % str(e))

    def __get_max_uidNumber(self):
        """
        查询 当前最大的uid，这个是在添加用户时，用于自增uid
        :param: None
        :return: max uidNumber
        """
        obj = self.ldapconn
        obj.protocal_version = ldap.VERSION3
        searchScope = ldap.SCOPE_SUBTREE
        retrieveAttributes = ['uidNumber']
        searchFilter = "uid=*"

        try:
            ldap_result = obj.search(
                base="%s" % self.base_dn,
                scope=searchScope,
                filterstr=searchFilter,
                attrlist=retrieveAttributes
            )
            print(ldap_result)
            result_set = []
            while True:
                result_type, result_data = obj.result(ldap_result, 0)
                if not result_data:
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(int(result_data[0][1].get('uidNumber')[0]))
            return max(result_set) + 1
        except ldap.LDAPError as e:
            logger.error('获取最大uid失败，原因为: %s' % str(e))

    def ldap_add_user(self, cn, mail, username, password):
        """
        添加ldap用户
        :param cn: 中文名, mail: 邮箱, username: 用户名, password: 密码
        :return: True/None
        """
        result = None
        try:
            obj = self.ldapconn
            obj.protocal_version = ldap.VERSION3
            password_encrypt = pass_encrypt(password)
            addDN = "uid=%s,%s" % (username, BASE_DN)
            attrs = {}
            attrs['objectclass'] = ['inetOrgPerson'.encode('utf-8')]
            attrs['cn'] = [str(cn).encode('utf-8')]
            # attrs['homeDirectory'] = str('/home/%s' % username)
            # attrs['loginShell'] = '/bin/bash'
            attrs['mail'] = [str(mail).encode('utf-8')]
            attrs['sn'] = [str(username).encode('utf-8')]
            attrs['uid'] = [str(username).encode('utf-8')]
            attrs['userPassword'] = [str(password_encrypt).encode('utf-8')]
            # attrs['uidNumber'] = str(self.__get_max_uidNumber())
            # attrs['gidNumber'] = self.__ldap_getgid(cn='员工')
            ldif = ldap.modlist.addModlist(attrs)
            obj.add_s(addDN, ldif)
            obj.unbind_s()
            result = True
        except ldap.LDAPError as e:
            logger.error("生成用户%s 失败，原因为: %s" % (username, str(e)))
        return result

    def check_user_belong_to_group(self, uid, group_cn='员工'):
        """
        查询 用户 是否归属于某个组
        :param uid: 用户uid , Ex: 'ssoadmin'
        :param group_cn: 归属组cn , Ex: '黑名单'
        :return: True|None
        """
        result = None
        try:
            search = self.ldap_search_dn(value=group_cn, value_type='cn')
            if search is None:
                raise ldap.LDAPError('未查询到相应 id')

            member_list = search[0][1].get('memberUid', [])
            if uid in member_list:
                result = True
        except ldap.LDAPError as e:
            logger.error('获取用户%s与组%s关系失败，原因为: %s' % (uid, group_cn, str(e)))
        return result

    def check_user_status(self, uid):
        """
        验证用户状态
        :param uid: 用户uid
        :return: 200: 用户可用
                 404: 用户不存在
                 403: 用户被禁用
        """
        result = 404
        data = None
        try:
            target_cn = self.ldap_get_user(uid=uid)
            if target_cn is None:  # 如未查到用户，记录日志，但不算错误，后边有很多地方会验证用户是否存在
                result = 404
                logger.debug("%s uid未查询到" % uid)
            else:
                if self.check_user_belong_to_group(uid=uid, group_cn='黑名单'):
                    result = 403
                else:
                    result, data = 200, target_cn
        except ldap.LDAPError as e:
            logger.error("%s 检查用户状态失败，原因为: %s" % (uid, str(e)))
            return 500
        return result, data

    def ldap_get_vaild(self, uid=None, passwd=None):
        obj = self.ldapconn
        target_cn = self.ldap_search_dn(value=uid)[0][0]
        print(target_cn)
        try:
            if obj.simple_bind_s(target_cn, passwd):
                return True
            else:
                return False
        except ldap.LDAPError as e:
            print(e)
            return False

    def ldap_update_password(self, uid, new_password=None, old_password=None):
        """
        更新密码
        :param uid: 用户uid，新password
        :return: True|None
        """
        result = None
        try:
            obj = self.ldapconn
            obj.protocal_version = ldap.VERSION3
            modifyDN = "uid=%s,%s" % (uid, BASE_DN)
            new_password_encrypt = pass_encrypt(new_password)
            #有old_password情况下
            if old_password:
                obj.passwd_s(modifyDN, [str(old_password).encode('utf-8')], [new_password_encrypt.encode('utf-8')])
                result = True
            else:
                obj.modify_s(modifyDN, [(ldap.MOD_REPLACE, 'userPassword', [new_password_encrypt.encode('utf-8')])])
                result = True
            obj.unbind_s()
        except ldap.LDAPError as e:
            logger.error("%s 密码更新失败，原因为: %s" % (uid, str(e)))
            return False
        return result

    def ldap_update_user(self, uid, old, new):
        """
        修改dap用户
        :param uid: 用户名
        :param old: 原属性 {'mail': ['admin@example.com']}
        :param new  新属性 {'mail': ['root@example.com']}
        :return: True/None
        """
        result = None
        try:
            obj = self.ldapconn
            obj.protocal_version = ldap.VERSION3
            dn = "uid=%s,%s" % (uid, BASE_DN)
            ldif = modlist.modifyModlist(old, new)
            obj.modify_s(dn, ldif)
            obj.unbind_s()
            result = True
        except ldap.LDAPError as e:
            logger.error("修改用户%s 失败，原因为: %s" % (uid, str(e)))
        return result


def main():
    # ldap = LDAPTool()
    # print(ldap.ldap_get_user('test'))
    pass

if __name__ == '__main__':
    main()