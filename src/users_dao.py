"""
DAO (Data Access Object) file

Helper file containing functions for accessing authentication data
in the database
"""

from db import db, User

def get_user_by_username(username):
    """
    Returns the user with the given username
    """
    return User.query.filter(User.username == username).first()

def get_user_by_session_token(session_token):
    """
    Returns the user with the given session token
    """
    return User.query.filter(User.session_token == session_token).first()

def get_user_by_refresh_token(refresh_token):
    """
    Returns the user with the given refresh token
    """
    return User.query.filter(User.refresh_token == refresh_token).first()

def verify_credentials(username, password):
    """
    Returns true if the credentials match, false otherwise
    """
    possible_user = get_user_by_username(username)

    if possible_user is None:
        return False, None
    return possible_user.verify_password(password), possible_user

def create_user(name, username, email, password):
    """
    Creates a User object with the given name, username, email, password
    """
    possible_user = get_user_by_username(username)

    if possible_user is not None:
        return False, possible_user
    
    user = User(
        name=name,
        username=username,
        email=email,
        password=password
    )
    db.session.add(user)
    db.session.commit()
    return True, user

def renew_session(refresh_token):
    """
    Renews the session of the user with given the refresh token
    """
    possible_user = get_user_by_refresh_token(refresh_token)
    if possible_user is None:
        raise Exception("Invalid refresh token")
    possible_user.renew_session()
    db.session.commit()
    return possible_user