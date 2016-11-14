from app import db

from .meta_instance import PostCat, PostTag


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    title_slug = db.Column(db.String)

    _tag_instances = db.relationship('PostTag',
                                     foreign_keys=[PostTag.tag_id],
                                     backref=db.backref('post', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')

    _cat_instances = db.relationship('PostCat',
                                     foreign_keys=[PostCat.cat_id],
                                     backref=db.backref('post', lazy='joined'),
                                     lazy='dynamic',
                                     cascade='all, delete-orphan')

    abstract = db.Column(db.Text)
    content = db.Column(db.Text)
    status = db.Column(db.String)
    publish_date = db.Column(db.DateTime)
    edit_date = db.Column(db.DateTime)
    draft = db.relationship()

    @property
    def tags(self):
        return [instance.tag for instance in self._tag_instances.all()]

    @tags.setter
    def tags(self, value):
        pass

    @property
    def categories(self):
        return [instance.category for instance in self._cat_instances.all()]

    @categories.setter
    def categories(self, value):
        pass

    def save(self):
        pass

    def publish(self):
        pass
