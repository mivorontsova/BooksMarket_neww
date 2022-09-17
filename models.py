from flask_login import UserMixin
from config import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    house = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    anonce = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Product %r>' % self.id


class Profiles(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    psw = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Profiles %r>' % self.id



class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    psw = db.Column(db.String, nullable=False)

    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'))

    def __repr__(self):
        return '<Users %r>' % self.name


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    msg = db.Column(db.Text)
    name = db.Column(db.String)

    username = db.Column(db.String, db.ForeignKey('profiles.username'))

    def __repr__(self):
        return '<Profiles %r>' % self.id


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    live = db.Column(db.String(500), nullable=False)
    state = db.Column(db.String(500), nullable=False)

    product = db.Column(db.Integer, db.ForeignKey('product.id'))
    login = db.Column(db.String, db.ForeignKey('users.id'))
    delivary = db.Column(db.String, db.ForeignKey('delivary.name'))

    def __repr__(self):
        return f"<orders {self.id}>"


class Delivary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    login = db.Column(db.String(20), nullable=False)
    number = db.Column(db.String(11), unique=True)
    days = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    about = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<delivary %r>' % self.name


class ProductAccept(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(500), nullable=False)

    id_prod = db.Column(db.Integer, db.ForeignKey('product.id'))
    username = db.Column(db.Integer, db.ForeignKey('users.username'))

    def __repr__(self):
        return '<cart %r>' % self.id
