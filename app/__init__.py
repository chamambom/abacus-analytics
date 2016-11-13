from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from flask_login import LoginManager

# Create an Instance of Flask
application = Flask(__name__)

# Include config from config.py
application.config.from_object('config')
application.secret_key = 'A0Zr98jh/3yXR~XHH!jmN]LWX/,?RT'

mail = Mail()
mail.init_app(application)

# Create an instance of SQLAlchemy
db = SQLAlchemy(application)

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'
login_manager.login_message = u"Please log in to access this page."
login_manager.login_message_category = "info"

# Import views to enable proper routing
from app import views, models
