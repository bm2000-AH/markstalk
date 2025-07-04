from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class PlaceForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    latitude = FloatField('Широта', validators=[DataRequired()])
    longitude = FloatField('Долгота', validators=[DataRequired()])
    price = IntegerField('Цена (₽)', validators=[DataRequired()])
    image = FileField('Фото (необязательно)', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Опубликовать')

class ReviewForm(FlaskForm):
    text = TextAreaField('Отзыв', validators=[DataRequired()])
    rating = IntegerField('Оценка от 1 до 5', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Оставить отзыв')

class ComplaintForm(FlaskForm):
    text = TextAreaField('Жалоба', validators=[DataRequired()])
    submit = SubmitField('Пожаловаться')

class ResponseForm(FlaskForm):
    response = TextAreaField('Ответ', validators=[DataRequired()])
    submit = SubmitField('Отправить')

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class MessageForm(FlaskForm):
    body = TextAreaField('Сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')

