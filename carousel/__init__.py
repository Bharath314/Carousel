from flask import Flask, render_template, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

class carousel_user:
    def __init__(self):
        self.is_authenticated = False
        self.user_id = None
        self.username = None
        self.display_picture = 'static/profile_pictures/default.png'
    def login(self, user):
        self.is_authenticated = True
        self.user_id = user.id
        self.username = user.username
        self.display_picture = url_for('static', filename = 'profile_pictures/' + user.display_picture)
    def logout(self):
        self.is_authenticated = False
        self.username = None
        self.user_id = None
        self.display_picture = 'default.png'
    def __repr__(self) -> str:
        return f"User('{self.username}', {self.is_authenticated}, '{self.display_picture}'"   

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
db.init_app(app)



from carousel import routes
    
