from app.models import Post, Tag, Category, Settings, User, Task, Flow
from app import create_app, db
from config import BASE_DIR
import os
import json
from datetime import datetime

TRUE = [1, '1', 'true', 'True', True, 'On', 'on']


def read_json(target_dir, version_name=None):
    data = dict()
    files = os.listdir(target_dir)
    if not version_name:
        version_name = sorted(files)[-1]
    else:
        for file in files:
            if version_name in file:
                version_name = file
    print(version_name)
    json_file = os.path.join(target_dir, version_name + '/database.json')
    with open(json_file, 'r') as f:
        data = json.loads(f.read())
    return data


def run():
    app = create_app("debug")

    with app.app_context():
        target_dir = os.path.abspath(os.path.join(BASE_DIR, 'database/backup'))
        database = read_json(target_dir)
        settings_data = database.get('Settings')
        users_data = database.get('User')
        posts_data = database.get('Post')
        tags_data = database.get('Tag')
        categories_data = database.get('Category')
        tasks_data = database.get('Task')
        flows_data = database.get('Flow')

        if settings_data:
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

        if users_data:
            for user in users_data:
                u = User(
                    _email=user.get("email"),
                    _name=user.get("name"),
                    _is_administrator=user.get("is_administrator"),
                    _password_hash=user.get("password_hash")
                )
                db.session.add(u)

        if posts_data:
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

        if users_data:
            for tag in tags_data:
                t = Tag(
                    _name=tag.get('name'),
                    _link=tag.get('link'),
                    _posts_count=tag.get('posts_count', 0),
                )
                db.session.add(t)

        if categories_data:
            for category in categories_data:
                c = Category(
                    _name=category.get('name'),
                    _link=category.get('link'),
                    _level=category.get('level'),
                    _order=category.get('order'),
                    _posts_count=category.get('posts_count', 0),
                )
                db.session.add(c)

        if tasks_data:
            for task in tasks_data:
                t = Task(
                    _text=task.get('text'),
                    _level=task.get('level'),
                    _status=task.get('status'),
                    _start=datetime.strptime(task.get('start'), "%Y-%m-%d %H:%M:%S"),
                    _finish=datetime.strptime(task.get('finish'), "%Y-%m-%d %H:%M:%S") if task.get('finish') else None,
                    _idea=task.get('idea', db.Text),
                    _flow_index=task.get('flow_index'),
                    _flow_order=task.get('flow_order'),
                )
                db.session.add(t)

        if flows_data:
            for flow in flows_data:
                f = Flow(
                    _text=flow.get('text'),
                    _task=flow.get('task'),
                    _fake_id=flow.get('fake_id')
                )
                db.session.add(f)
        db.session.commit()
