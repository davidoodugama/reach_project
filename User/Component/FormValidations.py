from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

class FormValidation(Form):
    def register(self, form):
        name = StringField('name', [validators.Length(min=5, max=50)])
        username = StringField('username', [validators.Length(min=5, max=50)])
        email = StringField('email', [validators.Length(min=6, max=50)])
        password = PasswordField('password', [validators.DataRequired(), validators.EqualTo("confirm", message="Password do not match")])
        confirm = PasswordField('Confirm Password')