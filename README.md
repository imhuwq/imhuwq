# 一.简介
基于Flask的个人博客，完全出于学习练手的目的。所以折腾第一， 开发效率第二。  
app基于Flask， 数据库为postgreSQL，也支持sqlite；  
服务器为tornado， middleware为nginx。  

把自己接触到的东西尽量在这个项目里面尝试；  
再根据自己建一个博客的需要，留下合适的东西。  

# 二. 使用

## 1. 获取程序
直接 `git clone` 获取程序代码  

## 2. 安装依赖
2.1 python包依赖
  - 首先安装虚拟环境`virtualenv`

  - `sudo apt install libffi-dev`，主要是用来支持misaka渲染markdown

  - 在激活虚拟环境的状态下 `pip install -r requirements.txt`

2.2 系统依赖
  - 安装postgreSQL
  - 安装和配置nginx  
  以下是参考nginx配置
  */etc/nginx/sites-available/default*
  ```nginx
  server {
      listen 80 default_server;
      listen [::]:80 default_server;
      server_name localhost;

      # 此处替换下行中的your_domain.access为你的网站域名
      access_log  /var/log/nginx/your_domain.com.access.log;

      # 此处替换下行中的路径为您的应用文件夹路径(manage.py等文件所在目录)
      root /home/yourname/sites/imhuwq;

      location /static/ {
      		 expires max;
      		 add_header Last-Modified $sent_http_Expires;
           # 此处替换下行中的路径为您的应用静态文件夹路径
      		 alias /home/yourname/sites/imhuwq/app/static/;
      }

      location / {
      			try_files $uri @tornado;
      }

      location @tornado {
      			proxy_set_header Host $host;
      			proxy_set_header X-Real-IP $remote_addr;
      			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      			proxy_pass       http://127.0.0.1:5000;
      }
  }
  ```
配置 nginx 后记得重启 nginx 服务。  

## 3 编辑配置文件
复制`config-sample.py`为`config.py`, 根据里面的文字提示来进行修改。  
在没有配置postgreSQL数据库的情况下默认使用sqlite。  

## 4. 创建数据库  
 4.1  在数据库命令行界面自行建立数据库和数据库用户  

 4.2 根据程序生成数据库表格  
```shell
cd imhuwq
source env/bin/activate
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```
## 5. 运行程序
可以直接执行:
```shell
python run.py
```

更推荐加入开机自启，以及自动重启:  

*/etc/init/tornado.your-site.com.conf*
```conf
description "Tornado server for www.your-site.com"

start on net-device-up
stop on shutdown

respawn

setuid your-user-name

chdir /home/yourname/sites/imhuwq.com
exec ./env/bin/python run.py

```
然后执行:
```shell
sudo start tornado.your-site.com.conf
```

# 三. Changelog
## v0.2
 - Todo 功能上线  
 登陆后默认进入Todo页面，可以增加四种等级的Task   
 flow 模式聚焦某个 Task， 可以分解子步骤，可以自由添加笔记  
 使用了非常多的 jquery 和 ajax， 操作非常方便

 - 博客优化
 数据库从 mysql 转移到 postgresql  
 博客的Markdown有代码高亮了，基于Pygments
 数据库表一律按功能增加前缀  
 博客的测试更加系统  

## v0.1
 - 日志编辑器  
 可通过ajax实时添加分类和标签；  
 可以设置评论开关和是否对外可见；  
 每篇文章可以保存一个草稿。  

 - 排版
 Markdown 基于 flask-misaka；  
 代码高亮基于 Pygments；

 - 分类和标签  
 每个分类可以有一个父分类和无数个子分类；  
 属于子分类的文章同样属于子分类的父分类；  
 多标签。  

 - 比较完善的文章管理后台  
 支持通过分类、标签、是否对外可见、是否可评论这些条件进行筛选；  
 支持批量删除文章，批量增、删、重置分类和标签；  
 批量打开/关闭评论以及批量公开/转为私密  

 - 使用disqus评论平台  

 - 使用google analytics 数据分析  

 - 首页可选择显示摘要还是全文，可设置每页最多文章篇数  

 - sitemap支持  

# 4.后期的打算
  - 支持图片   
  - 批量导出文章为markdown  
  - Todo 增加“项目”功能
  - News feed： 微博, 知乎, twitter， google+ 等社交媒体信息聚合
  - 有可能转到 Tornado 框架
