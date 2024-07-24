from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class UserProfileForm(FlaskForm):
    preferred_subject = StringField('Preferred Subject', validators=[DataRequired()])
    learning_style = SelectField('Learning Style', choices=[
        ('Visual', 'Visual'),
        ('Reading/Writing', 'Reading/Writing'),
        ('In-person', 'In-person')
    ], validators=[DataRequired()])
    strengths = TextAreaField('Strengths')
    weaknesses = TextAreaField('Weaknesses')
    submit = SubmitField('Update Profile')
