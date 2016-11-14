from app import db

from .meta_instance import PostTag

class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    name_slug = db.Column(db.String)
    _post_instances = db.relationship('PostTag',
                                      foreign_keys=[PostTag.post_id],
                                      backref=db.backref('tag', lazy='joined'),
                                      lazy='dynamic',
                                      cascade='all, delete-orphan')

    @property
    def posts(self):
        return
