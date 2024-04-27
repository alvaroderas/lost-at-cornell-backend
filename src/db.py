import datetime
import hashlib
import os
import bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """
    User Model
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User information
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password_digest = db.Column(db.String, nullable=False)
    posts = db.relationship("Post", cascade="delete")

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=False)
    session_expiration = db.Column(db.DateTime, nullable=False, unique=False)
    refresh_token = db.Column(db.String, nullable=False, unique=False)

    def __init__(self, **kwargs):
        """
        Initializes a user object
        """
        self.name = kwargs.get("name")
        self.username = kwargs.get("username")
        self.email = kwargs.get("email")
        self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.renew_session()

    def _urlsafe_base_64(self):
        """
        Randomly generates session and refreshes tokens
        """
        return hashlib.shal(os.urandom(64)).hexdigest()
    
    def renew_session(self):
        """
        Generates new tokens and resets expiration time
        """
        self.session_token = self._urlsafe_base_64()
        self.refresh_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(days=1)

    def verify_password(self, password):
        """
        Verifies the given password
        """
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)
    
    def verify_session_token(self, session_token):
        """
        Checks if session token is valid and hasn't expired
        """
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration
    
    def verify_refresh_token(self, refresh_token):
        """
        Checks if refresh token is valid
        """
        return refresh_token == self.refresh_token
    
    def serialize(self):
        """
        Serializes a User object without password
        """
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "posts": [p.simple_serialize() for p in self.posts]
        }

class Post(db.Model):
    """
    Post model
    """
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a Post object
        """
        self.description = kwargs.get("description")
        self.user_id = kwargs.get("user_id")
    
    def serialize(self):
        """
        Serialize a Post object
        """
        return {
            "id": self.id,
            "description": self.description,
            "user_id": self.user_id
        }
