from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'une_clé_secrète'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookly.db'

from . import routes
