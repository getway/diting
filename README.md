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

欢迎有兴趣的同学一起开发，联系我：
xiaomaoxue@gmail.com


[![运维导航](docs/_static/img/navi.png)](https://www.python.org/)

[![导航列表](docs/_static/img/navilist.png)](https://www.python.org/)

[![导航详情](docs/_static/img/navidetail.png)](https://www.python.org/)

[![导航创建](docs/_static/img/navicreate.png)](https://www.python.org/)

## 安装说明
需要基本环境Python3.6
项目路径: {install path}
首先配置config.py 主要配置数据库地址

```
注意：需要python3.6支持
cd {install path}/
#安装依赖
pip install -r requirements/requirements.txt
#生成数据库
python3 ../apps/manage.py makemigrations
python3 ../apps/manage.py migrate
#启动
python3 run_server.py 或 ./dt start
```
