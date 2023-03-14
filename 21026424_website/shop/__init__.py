from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '1f23be20dc146bed7459117b7dde327d037f5e6c32d469ae'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from shop import routes
