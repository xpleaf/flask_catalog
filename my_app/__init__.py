import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_wtf.csrf import CsrfProtect
from redis import Redis


ALLOWED_EXTENSTIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
app.secret_key = 'some_random_key' # key for flash message
app.config['WTF_CSRF_SECRET_KEY'] = 'random key for form'
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') + \
    '/my_app/static/uploads'
CsrfProtect(app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
redis = Redis()
app.debug = True

manager = Manager(app)
manager.add_command('db', MigrateCommand)


from my_app.catalog.views import catalog
from . import errors
app.register_blueprint(catalog)


db.create_all()
