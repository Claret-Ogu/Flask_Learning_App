from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class ItemForm(FlaskForm):
    """Form for creating/editing items"""
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=1, max=100, message='Name must be between 1 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=500, message='Description cannot exceed 500 characters')
    ])
    submit = SubmitField('Save')