from flask import Flask
from flask_mail import Message, Mail

application = Flask(__name__)
mail = Mail()
mail.init_app(application)

application.secret_key = 'A0Zr98jh/3yXR~XHH!jmN]LWX/,?RT'
application.config["MAIL_SERVER"] = "smtp.gmail.com"
application.config["MAIL_PORT"] = 465
application.config["MAIL_USE_SSL"] = True
application.config["MAIL_USERNAME"] = 'chamambom@gmail.com'
application.config["MAIL_PASSWORD"] = 'beautiful'


SECURITY_EMAIL_SENDER = 'chamambom@gmail.com'
RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
RECAPTCHA_DATA_ATTRS = {'theme': 'light'}
application.config.from_object(__name__)

