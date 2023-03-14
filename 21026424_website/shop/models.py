from datetime import datetime
from shop import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.Text, nullable = False)
    description = db.Column(db.Text, nullable = False)
    image_file = db.Column(db.String(40), nullable = False, default = 'default.png')
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    price = db.Column(db.Float, nullable = False)
    footprint = db.Column(db.Float, nullable = False)
    stock = db.Column(db.Integer, nullable = False, default = 50)

    def __repr__(self):
        return f"Item('{self.name}', '{self.description}')"

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), nullable=True)
    item = db.relationship('Item', backref = 'user', lazy=True)
    cart = db.Column(db.Text)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError("Password is not readable.")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_sales = db.Column(db.Integer)
    recommendations = db.Column(db.Integer)
    sale_rec_ratio = db.Column(db.Float)
    reviews = db.Column(db.Text)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
