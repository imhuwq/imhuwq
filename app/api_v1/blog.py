from flask import Blueprint, request, jsonify

blog_v1 = Blueprint('blog', __name__)


@blog_v1.route('/')
def index():
    return jsonify(status='ok',
                   page='blog index')


@blog_v1.route('/posts/')
def posts():
    return jsonify(status='ok',
                   page='all posts')


@blog_v1.route('/post/<title_slug>/')
@blog_v1.route('/category/<path:category_and_post_slug>/')
@blog_v1.route('/tag/<path:tag_and_post_slug>/')
@blog_v1.route('/archive/<path:date_and_post_slug>/')
def post(title_slug=None, category_and_post_slug=None, tag_and_post_slug=None, date_and_post_slug=None):
    if category_and_post_slug:
        return jsonify(status='ok',
                       page='single post by category and post title <%s>' % category_and_post_slug)
    elif tag_and_post_slug:
        return jsonify(status='ok',
                       page='single post by tag and post title <%s>' % tag_and_post_slug)
    elif date_and_post_slug:
        return jsonify(status='ok',
                       page='single post by date and post title <%s>' % date_and_post_slug)
    elif title_slug:
        return jsonify(status='ok',
                       page='single post by title <%s>' % title_slug)


@blog_v1.route('/categories/')
def categories():
    return jsonify(status='ok',
                   page='all categories')


@blog_v1.route('/categories/<path:category_slug>/')
def category(category_slug):
    return jsonify(status='ok',
                   page='post list of category <%s>' % category_slug)


@blog_v1.route('/tags/')
def tags():
    return jsonify(status='ok',
                   page='all tags')


@blog_v1.route('/tags/<tag_slug>/')
def tag(tag_slug):
    return jsonify(status='ok',
                   page='post list of tag <%s>' % tag_slug)


@blog_v1.route('/archives/')
def archives():
    return jsonify(status='ok',
                   page='all post archive')


@blog_v1.route('/archives/<path:date>/')
def archive(date):
    return jsonify(status='ok',
                   page='post archive of date <%s>' % date)


@blog_v1.route('/search')
def search():
    key_words = request.args.get('kw')
    return jsonify(status='ok',
                   kw=key_words)


@blog_v1.route('/posts/create', methods=['POST'])
def create_post():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/posts/edit', methods=['POST'])
def edit_post():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/posts/delete', methods=['POST'])
def delete_post():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/posts/categorize', methods=['POST'])
def categorize_post():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/posts/tag', methods=['POST'])
def tag_post():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/categories/create', methods=['POST'])
def create_category():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/categories/edit', methods=['POST'])
def edit_category():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/categories/delete', methods=['POST'])
def delete_category():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/categories/move', methods=['POST'])
def move_category():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/categories/merge', methods=['POST'])
def merge_category():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/tags/create', methods=['POST'])
def create_tag():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/tags/edit', methods=['POST'])
def edit_tag():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/tags/delete', methods=['POST'])
def delete_tag():
    json_data = request.get_json()
    return jsonify(json_data)


@blog_v1.route('/tags/merge', methods=['POST'])
def merge_tag():
    json_data = request.get_json()
    return jsonify(json_data)
