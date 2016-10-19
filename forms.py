from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, validators, ValidationError, PasswordField
from models import User


class ContactForm(Form):
    name = StringField("Name", [validators.DataRequired("Please enter your name.")])
    email = StringField("Email", [validators.DataRequired("Please enter your email address."),
                                  validators.Email("Please enter a valid email address.")])
    subject = StringField("Subject", [validators.DataRequired("Please enter a subject.")])
    message = TextAreaField("Message", [validators.DataRequired("Please enter a message.")])
    submit = SubmitField("Send")


class SignupForm(Form):
    email = StringField("Email", [validators.DataRequired("Please enter your email address."),
                                  validators.Email("Please enter a valid email address.")])
    # password = StringField("Password", [validators.DataRequired("Please enter your password.")])
    password = PasswordField('Password', [validators.DataRequired("Please enter a password.")])
    submit = SubmitField("Create account")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user:
            self.email.errors.append("Email is already taken")
            return False
        else:
            return True


class SigninForm(Form):
    email = StringField("Email", [validators.DataRequired("Please enter your email address."),
                                  validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.DataRequired("Please enter a password.")])
    submit = SubmitField("Sign In")

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append("Invalid e-mail or password")
            return False

# class RateIspService(Form):
#     metric_id = StringField('Metric Name', [validators.DataRequired("Metric Name is Required.")])
#     isp_id = StringField('ISP Name', [validators.DataRequired("Please enter ISP Name.")])
#     service_id = StringField('Service Name', [validators.DataRequired("Please enter Service Name.")])
#     ratings_value = StringField('Rating', [validators.DataRequired("Please enter Ratings.")])
#     custom_rating_comment = StringField('Comments', [validators.DataRequired("Please enter Your comments.")])
#     submit = SubmitField("Share your QOS Score")
#
#     def __init__(self, *args, **kwargs):
#         Form.__init__(self, *args, **kwargs)
#
#     def validate(self):
#         if not Form.validate(self):
#             return False
