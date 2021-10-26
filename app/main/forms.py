from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileSize
from wtforms import StringField, SubmitField, BooleanField, PasswordField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Имя пользователя: ", validators=[DataRequired("Некорректный логин"),
                                                             Length(min=4,
                                                                    max=100,
                                                                    message="Имя пользователя должно\
                                                                     быть от 4 до 25 символов"),
                                                             Regexp('^[A-Za-z][A-Za-z0-9_]*$', 0,
                                                                    'Имя пользователя должо содержать только\
                                                                    буквы, цифры и нижние подчеркивания.')])
    email = StringField('Email: ', validators=[DataRequired(), Email(message='Некорректный email')])
    password = PasswordField("Пароль: ",
                             validators=[DataRequired(),
                                         Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    confirm_password = PasswordField("Подтверждение пароля",
                                     validators=[DataRequired(), EqualTo("password", message='Пароли не совпадают')])
    submit = SubmitField("Зарегистрироваться")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first() or field.data == 'edit':
            raise ValidationError('Имя пользователся занято.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Данный email занят.')


class LoginForm(FlaskForm):
    username = StringField("Имя пользователя: ", validators=[DataRequired("Некорректный логин")])
    password = PasswordField("Пароль: ", validators=[DataRequired("Введите пароль")])
    remember = BooleanField("Запомнить", default=False)
    submit = SubmitField("Войти")


class UserEditForm(FlaskForm):
    first_name = StringField("Имя: ", validators=[Length(max=30, message='Превышено ограничение в 30 символов для поля: Имя.')])
    last_name = StringField("Фамилия: ", validators=[Length(max=30, message='Превышено ограничение в 30 символов для поля: Фамилия.')])
    about = TextAreaField('Рассказать что-нибудь о себе', validators=[Length(max=230, message='Превышено ограничение в 230 символов для поля: О себе.')])
    avatar = FileField()
    gender = SelectField(label="Пол: ", choices=['М', 'Ж'])
    submit = SubmitField('Подтвердить изменения')


class ImageForm(FlaskForm):
    avatar = FileField(label='Update Profile Picture', validators=[FileRequired(), FileAllowed(['jpeg', 'jpg', 'png', 'gif'])])
    submit = SubmitField('Загрузить')


class ArticleCreateForm(FlaskForm):
    title = StringField('Название статьи', validators=[DataRequired(), Length(max=60, message='Название не должно превышать 60 символов')])
    intro = TextAreaField('Описание статьи', validators=[DataRequired(), Length(max=230, message='Интро не должно превышать 230 символов')])
    text = TextAreaField('Содержимое статьи', validators=[DataRequired(), Length(max=30000, message='Интро не должно превышать 30000 символов')])
    able_to_comment = BooleanField('Разрешить оставлять комментарии?', default=False)
    submit = SubmitField("Опубликовать")


class ArticleEditForm(FlaskForm):
    title = StringField('Название статьи', validators=[DataRequired(), Length(max=60, message='Название не должно превышать 60 символов')])
    intro = TextAreaField('Описание статьи', validators=[DataRequired(), Length(max= 230, message='Интро не должно превышать 230 символов')])
    text = TextAreaField('Содержимое статьи', validators=[DataRequired(), Length(max=30000, message='Статья не должна превышать 30000 символов')])
    able_to_comment = BooleanField('Разрешить оставлять комментарии?')
    submit = SubmitField("Подтвердить")


class CreateCommentForm(FlaskForm):
    text = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField("Отправить")
