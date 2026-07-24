import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '217999cafb51d1333687bff1fb1e3836'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # 修复 BuildError: 确保使用 main.login
    login_manager.login_view = 'main.login' 
    login_manager.login_message_category = 'info'

    from uqnity_app.routes import main, page_not_found
    
    app.register_blueprint(main)
    
    app.register_error_handler(404, page_not_found)

    return app