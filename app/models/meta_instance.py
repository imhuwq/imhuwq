from app import db


class PostCat(db.Model):
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    cat_id = db.Column(db.Integer, db.ForeignKey('categories.id'), primary_key=True)
    joined_time = db.Column(db.DateTime)


class PostTag(db.Model):
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)
    joined_time = db.Column(db.DateTime)
