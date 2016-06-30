# 一.简介
基于Flask的个人博客，完全出于学习练手的目的。
所以折腾第一， 开发效率第二。
app基于Flask， 数据库为postgreSQL，也支持sqlite；
服务器为tornado， middleware为nginx。

## 1.整体方向
1.1 把自己接触到的东西尽量在这个项目里面尝试

1.2 再根据自己建一个博客的需要，留下合适的东西

## 2.目前情况

### 2.1关于数据库
可以选择postgreSQL数据库或者sqlite。当没有配置postgreSQL时默认使用sqlite；
博客中的数据库没有使用外键，关系全部写在model中；
只是听说外键会影响速度，但是查了一下也有说可以增加检索速度的；
既然是小博客，性能影响几乎没有，那就看个人喜好了。

### 2.2关于博客功能：
 2.2.1 日志编辑器
 可通过ajax实时添加分类和标签；
 可以设置评论开关和是否对外可见；
 每篇文章可以保存一个草稿。

 2.2.2 Markdown
 基于 flask-misaka。

 2.2.3 分类和标签
 每个分类可以有一个父分类和无数个子分类；
 属于子分类的文章同样属于子分类的父分类；
 多标签。

 2.2.4 比较完善的文章管理后台
 支持通过分类、标签、是否对外可见、是否可评论进行筛选；
 支持批量删除，批量增、删、重置分类和标签；
 批量打开/关闭评论以及批量公开/转为私密

 2.2.5 使用disqus评论平台

 2.2.6 使用google analytics 数据分析

 2.2.7 首页可选择显示摘要还是全文，可设置每页最多文章篇数

 2.2.8 sitemap支持

## 3.后期的跟进
 3.1. unit test等测试(已完成)
 3.2. 支持图片
 3.3. 支持主题(无限期搁置)
 3.4  持续的优化
 3.5  批量导出文章为markdown

# 二. 使用

## 1. 获取程序
直接 `git clone` 获取程序代码
## 2. 安装依赖
2.1 python包依赖
  - 首先安装虚拟环境`virtualenv`

  - `sudo apt install libffi-dev`，主要是用来支持misaka渲染markdown

  - 在激活虚拟环境的状态下 `pip install -r requirements.txt`

2.2 系统依赖
  - 安装mysql-server
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
      root /home/john/Desktop/imhuwq;

      location /static/ {
      		 expires max;
      		 add_header Last-Modified $sent_http_Expires;
           # 此处替换下行中的路径为您的应用静态文件夹路径
      		 alias /home/john/Desktop/imhuwq/app/static/;
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
2.3 创建数据库
  创建数据库的时候需要指定数据库的字符集为utf8
  ```mysql
  CREATE DATABASE your_db_name CHARACTER SET 'utf8';
  ```

## 3. 编辑配置文件
复制`config-sample.py`为`config.py`, 根据里面的文字提示来进行修改。
在没有配置mysql数据库的情况下默认使用sqlite。

## 4. 运行程序
4.1 激活虚拟环境

4.2 `python run.py`
