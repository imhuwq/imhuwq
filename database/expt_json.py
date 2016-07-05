from app.models import Post, Tag, Category, Settings
from app import create_app
import os, json

cur_dir = os.path.abspath(os.path.dirname(__file__))

app = create_app("debug")

with app.app_context():
    settings = Settings.query.all()
    settings_data = [{"site_admin_email": setting.site_admin_email,
                      "site_initiated": setting.site_initiated,
                      "enable_post_comment": setting.enable_post_comment,
                      "posts_per_page": setting.posts_per_page,
                      "show_abstract": setting.show_abstract,
                      "comments_per_page": setting.comments_per_page,
                      "site_title": setting.site_title,
                      "site_description": setting.site_description,
                      "disqus_identifier": setting.disqus_identifier,
                      "google_analytics_code": setting.google_analytics_code,
                      }
                     for setting in settings]

    posts = Post.query.all()
    posts_data = [{
                      'type': post._type,
                      'main_id': post._main_id,
                      'title': post._title,
                      'link': post._link,
                      'publish_date': str(post._publish_date.replace(microsecond=0)),
                      'edit_date': str(post._edit_date.replace(microsecond=0)),
                      'content': post._content,
                      'abstract': post._abstract,
                      'commendable': post._commendable,
                      'public': post._public,
                      'category': post._category,
                      'tags': post._tags,
                  }
                  for post in posts]

    tags = Tag.query.all()
    tags_data = [{
                     'name': tag._name,
                     'link': tag._link,
                     'posts_count': tag._posts_count,
                 }
                 for tag in tags]

    categories = Category.query.all()
    categories_data = [{
                           'name': category._name,
                           'link': category._link,
                           'level': category._level,
                           'order': category._order,
                           'posts_count': category._posts_count,
                       }
                       for category in categories]

    database = {
        'settings': settings_data,
        'posts': posts_data,
        'tags': tags_data,
        'categories': categories_data,
    }

    with open(cur_dir + '/database.json', 'w') as j:
        json.dump(database, j)
