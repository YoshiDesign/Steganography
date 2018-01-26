import os
import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import Form, SubmitField, TextAreaField, BooleanField, IntegerField, validators
from wtforms.csrf.core import CSRF
from wtforms.validators import DataRequired, Length, InputRequired


VALID_FILES = ('.png')

# Custom File-Type Validator
def file_type_check(form, field):
    filename = form.upload.data.filename
    if not os.path.splitext(field.data.filename)[1].lower() in VALID_FILES:
        raise validators.StopValidation('File must be in .png format.')

class User_Form(FlaskForm):

    upload = FileField(validators=[DataRequired(), file_type_check])
    message_area = TextAreaField('Secret Message', [validators.InputRequired()])
    verbose = BooleanField('Verbose-Mode')
    submit = SubmitField()

class Decode(FlaskForm):

    upload = FileField(validators=[DataRequired(), file_type_check])
    submit = SubmitField('Decode Your Image')