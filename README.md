## Diting 谛听系统
目标：让运维更简单

目前在jumpserver的框架下，开始项目
### 1 当前功能：
* 用户管理-用户增删改查
* 运维导航-快速链接、导航面板管理-增删改查
* 统一账户体系，支持LDAP登录、本地用户登录，开启LDAP的情况下，用户改密码实时同步到LDAP，新增用户直接可以添加到LDAP账户体系中
* LDAP账户修改一些属性同步到LDAP
### 2 待添加功能
* 导航权限分配
* 支持接入开源没有账户体系的系统
* 其他

欢迎有兴趣的同学一起开发，这里感谢[Jumpserver](https://github.com/jumpserver/)这么好的项目，借用了框架。



[![运维导航](docs/_static/img/dt-navis.png)](https://www.python.org/)

[![导航列表](docs/_static/img/dt-navi-list.png)](https://www.python.org/)

[![导航详情](docs/_static/img/dt-navi-detail.png)](https://www.python.org/)

[![用户管理](docs/_static/img/dt-users-manager.png)](https://www.python.org/)

[![用户管理](docs/_static/img/dt-ldap-manage.png)](https://www.python.org/)

## 3 安装说明
需要基本环境Python3.6
项目路径: {install path}
首先配置config.py 主要配置数据库地址

### 3.1 系统环境设置
```shell
# CentOS 7
$ setenforce 0  # 可以设置配置文件永久关闭
$ systemctl stop iptables.service
$ systemctl stop firewalld.service

# 修改字符集，否则可能报 input/output error的问题，因为日志里打印了中文
$ localedef -c -f UTF-8 -i zh_CN zh_CN.UTF-8
$ export LC_ALL=zh_CN.UTF-8
$ echo 'LANG=zh_CN.UTF-8' > /etc/locale.conf

# CentOS6
$ setenforce 0
$ service iptables stop

# 修改字符集，否则可能报 input/output error的问题，因为日志里打印了中文
$ localedef -c -f UTF-8 -i zh_CN zh_CN.UTF-8
$ export LC_ALL=zh_CN.UTF-8
$ echo 'LANG=zh_CN.UTF-8' > /etc/sysconfig/i18n
```

### 3.2 准备 Python3 和 Python 虚拟环境
```shell
#安装系统依赖
$ yum -y install wget sqlite-devel xz gcc automake zlib-devel openssl-devel epel-release git

#安装python3.6
$ wget https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tar.xz
$ tar xvf Python-3.6.1.tar.xz  && cd Python-3.6.1
$ ./configure && make && make install
# 这里必须执行编译安装，否则在安装 Python 库依赖时会有麻烦...

# 使用虚拟环境
$ /usr/local/bin/python3.6 -m venv /opt/venv3
$ source /opt/venv3/bin/active
#注意：当出现(venv3)时候，表示虚拟环境生成成功
$ (venv3) [root@xxx xxx]#
```

### 3.3 安装谛听(diting) 

```shell
#进入到安装目录/opt
$ cd /opt
$ git clone https://github.com/getway/diting.git
$ cd diting
# 安装依赖
$ pip install -r requirements/requirements.txt
# 数据库迁移(初始化数据库)
$ cd /opt/diting/utils
$ bash make_migrations.sh
#导入数据
$ cd /opt/diting/apps
$ python manage.py loaddata fixtures/init.json


```

### 3.4 服务启动

```shell
$ cd /opt/diting
#后台启动
$ ./dt start -d  或 python run_server.py

# 访问
http://127.0.0.1:8080
用户名 ： admin
密码： admin

```



