from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

# Provides a means of accessing functionality from Bcrypt()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    
    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        possible_user = User.query.filter_by(username=username).first()
        # If the username is already taken (True), then the method will return false. 
        # Otherwise, a new user instance will be created.
        if possible_user:
            return False
        else:
            hashed = bcrypt.generate_password_hash(pwd)
            hashed_utf8 = hashed.decode("utf8")
            return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
        
    
    @classmethod
    def authenticate(cls, username, pwd):
        # Returns true if the username provided exists in the database
        u = User.query.filter_by(username=username).first()
        # If the username exists and the password provided is the same as the hashed password
        # it will return the user instance (otherwise it will return False)
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False

class Feedback(db.Model):

    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @classmethod
    def add(cls, title, content, user_id):
        potential_user = User.query.filter(User.id == user_id)
        # If the user exists, the method will return a new feedback instance
        if potential_user:
            return cls(title=title, content=content, user_id=user_id)