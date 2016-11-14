from app import db

from .meta_instance import PostCat


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    base_36_id = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String)
    name_slug = db.Column(db.String)
    _post_instances = db.relationship('PostCat',
                                      foreign_keys=[PostCat.post_id],
                                      backref=db.backref('category', lazy='joined'),
                                      lazy='dynamic',
                                      cascade='all, delete-orphan')

    @property
    def posts(self):
        return

    @property
    def parent(self):
        return

    @property
    def children(self):
        return

    @property
    def descendants(self):
        return

    @property
    def ancestors(self):
        return
