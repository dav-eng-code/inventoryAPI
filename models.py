from datetime import datetime
from enum import unique
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Container(db.Model):
    __tablename__ = 'containers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),unique=True,nullable=False)
    location = db.Column(db.String(),nullable=False)
    container_value=db.Column(db.Integer,nullable=False,default=0)
    contents_value=db.Column(db.Integer,nullable=False,default=0)
    total_value = db.Column(db.Integer,nullable=False,default=0)
    items=db.relationship('Item',backref=db.backref('container',lazy=True))

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(),unique=True,nullable=False)
    tag = db.Column(db.String())
    location = db.Column(db.String(),nullable=False)  #item's location as indepenant item, but must take container locaiton when added to a location
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'))
    #container = db.relationship('Container',backref=db.backref('items',lazy=True))
    value = db.Column(db.Integer,nullable=False)
    status = db.Column(db.String(), nullable=False)
    date_updated = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()