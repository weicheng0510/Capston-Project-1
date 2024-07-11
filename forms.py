from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length

class UserForm(FlaskForm):
  """Form for sign up and login"""

  username = StringField('Username', validators=[InputRequired()])
  password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])


class CommentForm(FlaskForm):
  """Form for comment"""
  text = TextAreaField('Comments', validators=[InputRequired()], render_kw={"placeholder": "Leave a comment..."})
  recipe_title = HiddenField('Recipe Title')
