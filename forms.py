from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired, Length, URL, Email, EqualTo

csrf = CSRFProtect()


class CreateUserCost(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(min=3, max=80)])
    cover = StringField('Ссылка на обложку', validators=[DataRequired(), URL()])


class CreateItem(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(min=3, max=80)])
    value = StringField('Стоимость', validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    email = EmailField('Электронная почта', validators=[DataRequired()])
    nickname = StringField('Никнейм', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_confirmation = PasswordField('Пароль ещё раз', validators=[DataRequired(), EqualTo('password')])




