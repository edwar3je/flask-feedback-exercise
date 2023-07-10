from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, Email

class RegisterUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(message="Please provide a unique username no longer than 20 characters."), Length(max=20, message="Username can't be longer than 20 characters.")])
    password = PasswordField("Password", validators=[InputRequired(message="Please provide a password.")])
    email = EmailField("Email Address", validators=[InputRequired(message="Please provide a valid email address that's no longer than 50 characters."), Length(max=50, message="Email address can't be longer than 50 characters."), Email(message="Email provided is not valid.")])
    first_name = StringField("First Name", validators=[InputRequired(message="Please provide your first name."), Length(max=30, message="Name provided can't be longer than 30 characters.")])
    last_name = StringField("Last Name", validators=[InputRequired(message="Please provide your last name."), Length(max=30, message="Name provided can't be longer than 30 characters.")])

class LoginUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(message="Please provide your username."), Length(max=20, message="Username can't be longer than 20 characters.")])
    password = PasswordField("Password", validators=[InputRequired(message="Please provide your password.")])

class AddFeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(message="Please provide a title."), Length(max=100, message="Title can't be longer than 100 characters.")])
    content = StringField("Content", validators=[InputRequired(message="Please provide text for content.")])

class UpdateFeedbackForm(FlaskForm):
    # These fields have been made optional so that they can be left blank. If they are left blank, Flask will just 
    # assign the previous values to each field. The only thing to be concerned about is the max length of the title.
    title = StringField("Title", validators=[Length(max=100, message="Title can't be longer than 100 characters.")])
    content = StringField("Content")