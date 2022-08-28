"""
# VALIDATING REQUEST OBJECTS
#
# @author David Oodugama
# @email davidoodugama1999@gmail.com
# @version v1.0 2022-July-25
"""

from wtforms import Form, StringField, TextAreaField, PasswordField, validators, EmailField

class RegisterValidation(Form):
    name = StringField('name', [validators.Length(min = 5, max = 50)])
    username = StringField('username', [validators.Length(min = 5, max = 50)])
    email = EmailField('email', [validators.Length(min = 6, max = 50)])
    role = StringField('role', [validators.Length(min = 1, max = 15)])
    contact = StringField('email', [validators.Length(min = 10, message = "Invalid number. Number length should be 10.")])
    password = PasswordField('password', [validators.DataRequired(), validators.EqualTo("confirm", message = "Password do not match")])
    confirm = PasswordField('Confirm Password')