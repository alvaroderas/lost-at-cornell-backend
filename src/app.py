import json
from db import db, User, Post, Conversation, Message
from flask import Flask, request
import users_dao
import datetime
import bcrypt

app = Flask(__name__)
db_filename = "lost.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def extract_token(request):
    """
    Extracts the token from request
    """
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False, json.dumps({"error": "Missing Authorization header"})
    
    bearer_token = auth_header.replace("Bearer", "").strip()
    if not bearer_token:
        return False, json.dumps({"error": "Invalid Authorization header"})
    return True, bearer_token

def success_response(data, code=200):
    """
    Success response for good requests
    """
    return json.dumps(data), code

def failure_response(message, code=404):
    """
    Failure respponse for bad requests
    """
    return json.dumps({"error": message}), code

# Routes

# User authentication routes

@app.route("/api/users/register/", methods=["POST"])
def register_user():
    """
    Endpoint for registering a user
    """
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")
    if name is None or username is None or email is None or password is None:
        return failure_response("Invalid body", 400)
    created, user = users_dao.create_user(name, username, email, password)
    if not created:
        return failure_response("User already exists", 400)
    
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "refresh_token": user.refresh_token
    }, 201)

@app.route("/api/users/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    body = json.loads(request.data)
    username = body.get("username")
    password = body.get("password")

    if username is None or password is None:
        return failure_response("Invalid body", 400)
    
    success, user = users_dao.verify_credentials(username, password)
    if not success:
        return failure_response("Invalid credentials", 400)
    
    user.renew_session()
    db.session.commit()
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "refresh_token": user.refresh_token
    })

@app.route("/api/users/logout/", methods=["POST"])
def logout():
    """
    Endpoint for logging out a user
    """
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    user.session_expiration = datetime.datetime.now()
    db.session.commit()
    return success_response({"message": "You have been logged out"})

@app.route("/api/users/refresh/", methods=["POST"])
def renew_session():
    """
    Endpoint for renewing a session
    """
    success, response = extract_token(request)
    if not success:
        return response
    refresh_token = response

    try:
        user = users_dao.renew_session(refresh_token)
    except:
        return failure_response("Invalid refresh token", 400)
    
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "refresh_token": user.refresh_token
    })

# User routes

@app.route("/api/users/")
def get_all_users():
    """
    Endpoint for getting all users
    """
    return success_response({"users": [u.serialize() for u in User.query.all()]})

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())

@app.route("/api/users/edit/", methods=["POST"])
def edit_user():
    """
    Endpoint for editing a user's credentials by session token
    """
    body = json.loads(request.data)
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    name = body.get("name")
    username = body.get("username")
    email = body.get("email")
    password = body.get("password")
    if name is not None:
        user.name = name
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if password is not None:
        user.password_digest = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt(rounds=13))
    db.session.commit()
    return success_response(user.serialize())
    
@app.route("/api/users/delete/", methods=["DELETE"])
def delete_user():
    """
    Endpoint for deleting a user by session token
    """
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    db.session.delete(user)
    db.session.commit()
    return success_response(user.serialize())

# Post routes

@app.route("/api/users/<int:user_id>/posts/")
def get_posts_by_user(user_id):
    """
    Endpoint for getting all posts by user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response({"posts": [p.serialize() for p in user.posts]})

