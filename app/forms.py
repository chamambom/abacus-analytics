from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextAreaField, SubmitField, validators, PasswordField, SelectMultipleField, widgets
from app.models import User


class ContactForm(FlaskForm):
    name = StringField("Name", [validators.DataRequired("Please enter your name.")])
    email = StringField("Email",
                        [validators.DataRequired("Please enter your email address."),
                         validators.Email("Please enter a valid email address.")])
    subject = StringField("Subject", [validators.DataRequired("Please enter a subject.")])
    message = TextAreaField("Message", [validators.DataRequired("Please enter a message.")])
    submit = SubmitField("Send")


class SignupForm(FlaskForm):
    email = StringField("Email", [validators.DataRequired("Please enter your email address."),
                                  validators.Email("Please enter a valid email address.")])
    # password = StringField("Password", [validators.DataRequired("Please enter your password.")])
    password = PasswordField('Password', [validators.DataRequired("Please enter a password.")])
    recaptcha = RecaptchaField()
    submit = SubmitField("Create account")

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        user = User.query.filter_by(email=self.email.data.lower()).first()
        if user:
            self.email.errors.append("Email is already taken")
            return False
        else:
            return True


class LoginForm(FlaskForm):
    email = StringField("Email", [validators.DataRequired("Please enter your email address."),
                                  validators.Email("Please enter your email address.")])
    password = PasswordField('Password', [validators.DataRequired("Please enter a password.")])
    submit = SubmitField("Sign In")


data = [('value_a', 'Value A'), ('value_b', 'Value B'), ('value_c', 'Value C')]


class MultipleCheckBoxes(FlaskForm):
    example = SelectMultipleField(
        'Pick Things!',
        choices=data,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False)
    )
