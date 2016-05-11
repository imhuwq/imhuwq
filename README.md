# 一.简介
基于Flask的个人博客，完全出于学习练手的目的。  
所以折腾第一， 开发效率第二。  
app基于Flask， 数据库为mysql，也支持sqlite；  
服务器为tornado， middleware为nginx。

## 1.整体方向
1.1 把自己接触到的东西尽量在这个项目里面尝试  

1.2 再根据自己建一个博客的需要，留下合适的东西  

## 2.目前情况
 2.1 日志编辑器  
 支持保存草稿，可通过ajax实时添加分类和标签，可以设置评论开关和是否对外可见。  

 2.2 Markdown  
 基于 flask-misaka  

 2.3 多层级分类
 每个分类可以有一个父分类和无数个子分类。  
 属于子分类的文章同样属于子分类的父分类。  
 分类的family-tree基于material path。  一开始是实用的one-to-many关系，但是越级查询的时候很麻烦并且不符合直觉。比如查找分类A下的所有文章
 时，不仅要先查找A下面的文章，还要再找到A的子分类，以及子分类的子分类，以此类推，再找到所有后辈的文章，而使用Material Path的话，直接查找分
 类link是基于分类A的link的文章就好了:`Post.query.filter(Post.category_link.like(A.link+'/%')).all()`  
 分类的直属子父级关系有self-refrential的one-to-many数据库关系，主要是出于经常使用的一些功能的方便性考虑。  

 2.4 多标签  
 标签和文章之间也不是用的many-to-many的数据库关系，而是直接在文章数据库中记录标签字符串，再使用like查询。标签之间并没有层次关系，标签和文章
 之间有很清晰的多对多关系，而使用like据说对性能有影响。但不使用多对多关系，是出于保持和分类设计的一致性考虑，并且对于个人博客来说性能影响几乎
 没有...  

 2.5 比较完善的文章管理后台  
 支持通过分类、标签、是否对外可见、是否可评论进行筛选，支持批量删除，批量增、删、重置分类和标签，批量打开/关闭评论以及批量公开/转为私密  

 2.6 分类和标签管理  

 2.7 使用disqus评论平台  

## 3.后期的跟进
 3.1. unit test等测试  
 3.2. 支持图片  
 3.3. 支持主题  
 3.4  持续的优化  

## 4.终极展望
 4.1. 完备的博客  
 4.2. 基于个人兴趣的news feed  
 4.3. 基于文件夹的相册  
 4.4. TODO应用  


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
