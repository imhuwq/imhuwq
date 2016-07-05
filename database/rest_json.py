from app.models import Post, Tag, Category, Settings, User
from app import create_app, db
import os, json
from datetime import datetime

cur_dir = os.path.abspath(os.path.dirname(__file__))
TRUE = [1, '1', 'true', 'True', True, 'On', 'on']

app = create_app("debug")

email = input("请输入用户邮箱:")
name = input("请输入用户名:")
passwd = input("请输入用户密码:")

with app.app_context():
    user = User(email=email, name=name, password=passwd)
    db.session.add(user)
    db.session.commit()

    with open(cur_dir + '/database.json', 'r') as d:
        database = json.load(d)

    settings_data = database.get('settings')
    posts_data = database.get('posts')
    tags_data = database.get('tags')
    categories_data = database.get('categories')

    for setting in settings_data:
        sett = Settings(_site_admin_email=setting.get('site_admin_email'),
                        _site_initiated=setting.get('site_initiated') in TRUE,
                        _enable_post_comment=setting.get('enable_post_comment') in TRUE,
                        _posts_per_page=setting.get('posts_per_page'),
                        _show_abstract=setting.get('show_abstract'),
                        _comments_per_page=setting.get('comments_per_page'),
                        _site_title=setting.get('site_title'),
                        _site_description=setting.get('site_description'),
                        _disqus_identifier=setting.get('disqus_identifier'),
                        _google_analytics_code=setting.get('google_analytics_code'),
                        )
        db.session.add(sett)

    for post in posts_data:
        po = Post(_type=post.get('type'),
                  _main_id=post.get('main_id'),
                  _title=post.get('title'),
                  _link=post.get('link'),
                  _publish_date=datetime.strptime(post.get('publish_date'), "%Y-%m-%d %H:%M:%S"),
                  _edit_date=datetime.strptime(post.get('edit_date'), "%Y-%m-%d %H:%M:%S"),
                  _content=post.get('content'),
                  _abstract=post.get('abstract'),
                  _commendable=post.get('commendable'),
                  _public=post.get('public'),
                  _category=post.get('category'),
                  _tags=post.get('tags'),
                  )

        db.session.add(po)

    for tag in tags_data:
        t = Tag(
            _name=tag.get('name'),
            _link=tag.get('link'),
            _posts_count=tag.get('posts_count', 0),
        )
        db.session.add(t)

    for category in categories_data:
        c = Category(
            _name=category.get('name'),
            _link=category.get('link'),
            _level=category.get('level'),
            _order=category.get('order'),
            _posts_count=category.get('posts_count', 0),
        )
        db.session.add(c)

    db.session.commit()
