import json
from db import db, User, Post, Conversation, Message, Asset
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

@app.route("/api/users/session/", methods=["POST"])
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

@app.route("/")
def hello_world():
    """
    Endpoint for testing
    """
    return "Hello, world!"

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
    pfp = body.get("pfp")
    if name is not None:
        user.name = name
    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if password is not None:
        user.password_digest = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt(rounds=13))
    if pfp is not None:
        asset = Asset(image_data=pfp)
        user.pfp = asset
        db.session.add(asset)
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

@app.route("/api/posts/")
def get_all_posts():
    """
    Endpoint for getting all posts
    """
    return success_response({"posts": [p.serialize() for p in Post.query.all()]})

@app.route("/api/posts/<int:post_id>/")
def get_post(post_id):
    """
    Endpoint for getting a post by id
    """
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    return success_response(post.serialize())

@app.route("/api/posts/", methods=["POST"])
def create_post():
    """
    Endpoint for creating a post
    """
    body = json.loads(request.data)
    title = body.get("title")
    image = body.get("image")
    item = body.get("item")
    status = body.get("status")
    text = body.get("text")
    location = body.get("location")
    timestamp = datetime.datetime.now()

    if title is None or item is None or status is None or text is None or location is None:
        return failure_response("Invalid body", 400)
    
    if image is not None:
        asset = Asset(image_data=image)
        db.session.add(asset)
    
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    if image is not None:
        asset = Asset(image_data=image)
        db.session.add(asset)
        post = Post(
            title=title,
            image=asset,
            item=item,
            status=status,
            text=text,
            location=location,
            timestamp=timestamp,
            user_id=user.id
        )
    else:
        post = Post(
            title=title,
            image=None,
            item=item,
            status=status,
            text=text,
            location=location,
            timestamp=timestamp,
            user_id=user.id
        )
    db.session.add(post)
    db.session.commit()
    return success_response(post.serialize(), 201)

@app.route("/api/posts/<int:post_id>/", methods=["POST"])
def edit_post(post_id):
    """
    Endpoint for editing a post by id
    """
    body = json.loads(request.data)
    title = body.get("title")
    image = body.get("image")
    item = body.get("item")
    status = body.get("status")
    text = body.get("text")
    location = body.get("location")

    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")

    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    
    if post.user_id != user.id:
        return failure_response("Unauthorized", 401)
    
    if title is not None:
        post.title = title
    if item is not None:
        post.item = item
    if status is not None:
        post.status = status
    if text is not None:
        post.text = text
    if location is not None:
        post.location = location
    if image is not None:
        asset = Asset(image_data=image)
        post.image = asset
        db.session.add(asset)
    db.session.commit()
    return success_response(post.serialize())

@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def delete_post(post_id):
    """
    Endpoint for deleting a post by id
    """
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found")
    if post.user_id != user.id:
        return failure_response("Unauthorized", 401)
    
    db.session.delete(post)
    db.session.commit()
    return success_response(post.serialize())

# Conversation routes

@app.route("/api/users/<int:user_id>/convos/")
def get_conversations_by_user(user_id):
    """
    Endpoint for getting all conversations by user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response({"conversations": [c.serialize() for c in user.conversations]})

@app.route("/api/users/convos/<int:convo_id>/")
def get_conversation(convo_id):
    """
    Endpoint for getting a conversation by id
    """
    conversation = Conversation.query.filter_by(id=convo_id).first()
    if conversation is None:
        return failure_response("Conversation not found")
    return success_response(conversation.serialize())

@app.route("/api/users/convos/", methods=["POST"])
def create_conversation():
    """
    Endpoint for creating a conversation
    """
    body = json.loads(request.data)
    username = body.get("username")
    user2 = User.query.filter_by(username=username).first()
    if user2 is None:
        return failure_response("User not found")
    
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    conversation = Conversation(
        user1_id=user.id,
        user2_id=user2.id
    )

    db.session.add(conversation)
    db.session.commit()
    return success_response(conversation.serialize(), 201)

@app.route("/api/users/convos/<int:convo_id>/", methods=["DELETE"])
def delete_conversation(convo_id):
    """
    Endpoint for deleting a conversation by id
    """
    conversation = Conversation.query.filter_by(id=convo_id).first()
    if conversation is None:
        return failure_response("Conversation not found")
    
    db.session.delete(conversation)
    db.session.commit()
    return success_response(conversation.serialize())

# Message routes

@app.route("/api/users/convos/<int:convo_id>/messages/", methods=["POST"])
def send_message(convo_id):
    """
    Endpoint for sending a message
    """
    body = json.loads(request.data)
    receiver = body.get("receiver")
    content = body.get("content")
    timestamp = datetime.datetime.now()

    if receiver is None or content is None:
        return failure_response("Invalid body", 400)
    
    receiver_user = User.query.filter_by(username=receiver).first()

    if receiver_user is None:
        return failure_response("Receiver not found")
    
    conversation = Conversation.query.filter_by(id=convo_id).first()
    if conversation is None:
        return failure_response("Conversation not found")
    
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    if user.id != conversation.user1_id and user.id != conversation.user2_id:
        return failure_response("User not in conversation")
    
    
    message = Message(
        sender_id=user.id,
        receiver_id=receiver.id,
        content=content,
        timestamp=timestamp,
        conversation_id=convo_id
    )

    if user.id == conversation.user1_id:
        conversation.user1_messages.append(message)
    else:
        conversation.user2_messages.append(message)

    db.session.add(message)
    db.session.commit()
    return success_response(message.serialize(), 201)

@app.route("/api/users/convos/<int:convo_id>/messages/")
def get_messages(convo_id):
    """
    Endpoint for getting all messages in a conversation
    """
    conversation = Conversation.query.filter_by(id=convo_id).first()
    if conversation is None:
        return failure_response("Conversation not found")
    return success_response({
        "messages": [m.serialize() for m in Message.query.filter_by(conversation_id=convo_id).all()]
    })

@app.route("/api/users/convos/<int:convo_id>/user/")
def get_messages_from_logged_in_user(convo_id):
    """
    Endpoint for getting all messages by the current logged in
    user in the conversation
    """
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    conversation = Conversation.query.filter_by(id=convo_id).first()
    if conversation is None:
        return failure_response("Conversation not found")
    
    if user.id != conversation.user1_id and user.id != conversation.user2_id:
        return failure_response("User not in conversation")
    
    if user.id == conversation.user1_id:
        return success_response({
            "messages": [m.serialize() for m in conversation.user1_messages]
        })
    else:
        return success_response({
            "messages": [m.serialize() for m in conversation.user2_messages]
        })

@app.route("/api/users/convos/<int:convo_id>/other/")
def get_messages_from_other_user(convo_id):
    """
    Endpoint for getting all messages by the other user in the
    conversation
    """
    success, response = extract_token(request)
    if not success:
        return response
    session_token = response

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    
    conversation = Conversation.query.filter_by(id=convo_id).first()
    if conversation is None:
        return failure_response("Conversation not found")
    
    if user.id != conversation.user1_id and user.id != conversation.user2_id:
        return failure_response("User not in conversation")
    
    if user.id == conversation.user1_id:
        return success_response({
            "messages": [m.serialize() for m in conversation.user2_messages]
        })
    else:
        return success_response({
            "messages": [m.serialize() for m in conversation.user1_messages]
        })
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)