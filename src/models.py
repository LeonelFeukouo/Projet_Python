#CREATION DE LA STRUCTURE DES TABLES DE LA BD

from flask_login import UserMixin
from . import db
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    pseudo = db.Column(db.String(50), unique=True, nullable=False)
    createAt = db.Column(db.TIMESTAMP, default=datetime.now, nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='default.png')
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"User('{self.name}', '{self.surname}', '{self.pseudo}', '{self.createAt}', '{self.image_file}')"


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    signature = db.Column(db.Text, nullable=False)
    isRead = db.Column(db.Boolean, default=False, nullable=False)
    createAt = db.Column(db.TIMESTAMP, nullable=False)
    deleteAt = db.Column(db.Date)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship("User", backref="user", uselist=False, foreign_keys=[author_id])
    destination = db.relationship("User", backref="reference", uselist=False, foreign_keys=[destination_id])

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        self.createAt = datetime.now()

    def __repr__(self):
        return f"Message('{self.content}','{self.signature}', '{self.isRead}', '{self.createAt}')"
