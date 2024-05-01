import datetime
import hashlib
import os
import bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("conversation_id", db.Integer, db.ForeignKey("conversations.id"))
)

class User(db.Model):
    """
    User model
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User information
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)
    posts = db.relationship("Post", cascade="delete")
    conversations = db.relationship("Conversation", secondary=association_table, back_populates="users")
    # pfp

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
        return hashlib.sha1(os.urandom(64)).hexdigest()
    
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
            "posts": [p.serialize() for p in self.posts],
            "conversations": [c.serialize() for c in self.conversations]
        }
    

class Post(db.Model):
    """
    Post model
    """
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    # image
    item = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    text = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a Post object
        """
        self.title = kwargs.get("title")
        self.item = kwargs.get("item")
        self.status = kwargs.get("status")
        self.text = kwargs.get("text")
        self.location = kwargs.get("location")
        self.timestamp = kwargs.get("timestamp")
        self.user_id = kwargs.get("user_id")
    
    def serialize(self):
        """
        Serialize a Post object
        """
        return {
            "id": self.id,
            "title": self.title,
            "item": self.item,
            "status": self.status,
            "text": self.text,
            "location": self.location,
            "timestamp": str(self.timestamp),
            "user_id": self.user_id
        }


class Conversation(db.Model):
    """
    Conversation model
    """  
    __tablename__ = "conversations"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user1_messages = []
    user2_messages = []
    messages = db.relationship("Message", cascade="delete")
    user1_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    users = db.relationship("User", secondary=association_table, back_populates="conversations")

    def __init__(self, **kwargs):
        """
        Initialize a Conversation object
        """ 
        self.user1_id = kwargs.get("user1_id")
        self.user2_id = kwargs.get("user2_id")

    def serialize(self):
        """
        Serialize a Conversation object
        """
        return {
            "id": self.id,
            "user1_messages": [m.serialize() for m in self.user1_messages],
            "user2_messages": [m.serialize() for m in self.user2_messages],
            "user1_id": self.user1_id,
            "user2_id": self.user2_id
        }
    

class Message(db.Model):
    """
    Message model
    """
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a Message object
        """
        self.sender_id = kwargs.get("sender_id")
        self.receiver_id = kwargs.get("receiver_id")
        self.content = kwargs.get("content")
        self.timestamp = kwargs.get("timestamp")
        self.conversation_id = kwargs.get("conversation_id")

    def serialize(self):
        """
        Serialize a Message object
        """
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "timestamp": str(self.timestamp),
            "conversation_id": self.conversation_id
        }