from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from carousel.models import User



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=40)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one.')
    


class LoginForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=40)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')



class PostForm(FlaskForm):
    caption = TextAreaField('Caption',  validators=[DataRequired()])
    picture = FileField('Upload an image(Optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post')


class UpdateAccountForm(FlaskForm):
    def __init__(self, current_username,**kwargs ):
        super().__init__(**kwargs)
        self.current_username = current_username

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    display_picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != self.current_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')


class SearchBar(FlaskForm):
    def __init__(self, **kwargs ):
        super().__init__(**kwargs)
        self.users = [user.username for user in User.query.all()]
        print(self.users)
        self.search_results = []
    search_term = StringField('Search for users',
                              validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Search')
    def validate_search_term(self, search_term):
        print('--------------doing---------------')
        for username in self.users:
            if search_term.data.lower() in username.lower():
                self.search_results.append(username)
        if not self.search_results:
            raise ValidationError('No users found')




