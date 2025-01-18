from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, FileField, PasswordField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo


class AddArticleForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2)])
    text = TextAreaField("Text", validators=[DataRequired()])
    image = FileField("Image")
    submit = SubmitField("Add article")


class RegisterForm(FlaskForm):
    username = StringField("Enter your username", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Enter your password", validators=[DataRequired()])
    repeat_password = PasswordField("Repeat your password", validators=[DataRequired(), EqualTo("password", message="Passwords must match")])
    submit = SubmitField("Register")


class LogInForm(FlaskForm):
    username = StringField("Enter your username", validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField("Enter your password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class Survey(FlaskForm):
    name = StringField("Enter your name", validators=[DataRequired(), Length(min=2, max=50)])
    mail = EmailField("Enter your e-mail", validators=[DataRequired()])
    content = StringField("Text", validators=[DataRequired()])
    submit = SubmitField("Send")
