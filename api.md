# API Specification

Values wrapped in `< >` are placeholders for what the field values should be. Also be sure to read the request route carefully when you implement it.

## Deployed Base URL

`http://34.86.144.120/`

## Expected Functionality

## User Endpoints

### Register user

`POST /api/users/register/`

Request:

```json
{
  "name": "Alvaro Deras",
  "username": "aaderas",
  "email": "ad2226@cornell.edu",
  "password": "pass"
}
```

Response:

```json
{
    "session_token": <session_token>,
    "session_expiration": <session_expiration>,
    "refresh_token": <refresh_token>
}
```

### Login user

`POST /api/users/login/`

Request:

```json
{
  "username": "aaderas",
  "password": "pass"
}
```

Response:

```json
{
    "session_token": <session_token>,
    "session_expiration": <session_expiration>,
    "refresh_token": <refresh_token>
}
```

### Logout user

`POST /api/users/logout/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Response:

```json
{ "message": "You have been logged out" }
```

_Note:_

- If no user is found: `{"message": "Invalid session token"}`
- If user's session token is invalid:`{"message": "Invalid session token"}`

### Refresh session

`POST /api/users/session/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <refresh_token> |

Response:

```json
{
    "session_token": <session_token>,
    "session_expiration": <new session_expiration>,
    "refresh_token": <refresh_token>
}
```

### Get all users

`GET /api/users/`

Response:

```json
{
    "users": [
        {
            "id": 1,
            "name": "Alvaro Deras",
            "username": "aaderas",
            "email": "ad2226@cornell.edu",
            "pfp": <IMAGE URL (IF USER PROVIDED PFP)>,
            "posts": [<SERIALIZED POST>],
            "conversations": [<SERIALIZED CONVERSATION>]
        },
        ...
    ]
}
```

### Get user by id

`GET /api/users/<user_id>/`

Response:

```json
{
    "id": 1,
    "name": "Alvaro Deras",
    "username": "aaderas",
    "email": "ad2226@cornell.edu",
    "pfp": <IMAGE URL (IF USER PROVIDED PFP)>,
    "posts": [<SERIALIZED POST>],
    "conversations": [<SERIALIZED CONVERSATION>]
}
```

### Edit user information

`POST /api/users/edit/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Request:

```json
{
    "name": <USER INPUT (OPTIONAL)>,
    "username": <USER INPUT (OPTIONAL)>,
    "email": <USER INPUT (OPTIONAL)>,
    "pfp": <USER INPUT (OPTIONAL - MUST BE BASE64 ENCODED)>,
    "password": <USER INPUT (OPTIONAL)>
}
```

Response:

```json
{
    "id": <ID>,
    "name": <USER INPUT OR PREVIOUS NAME IF NOT PROVIDED>,
    "username": <USER INPUT OR PREVIOUS USERNAME IF NOT PROVIDED>,
    "email": <USER INPUT OR PREVIOUS EMAIL IF NOT PROVIDED>,
    "pfp": <IMAGE URL OR PREVIOUS IMAGE URL IF NOT PROVIDED>,
    "posts": [<SERIALIZED POST>],
    "conversations": [<SERIALIZED CONVERSATION>]
}
```

_Note:_

- The edit user endpoint works by editing the user that is currently logged in with a session token.

### Delete user

`DELETE /api/users/delete/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Response:

```json
{
    "id": <ID>,
    "name": <NAME> ,
    "username": <USERNAME>,
    "email": <EMAIL>,
    "pfp": <IMAGE URL>,
    "posts": [<SERIALIZED POST>],
    "conversations": [<SERIALIZED CONVERSATION>]
}
```

_Note:_

- The delete user endpoint works by deleting the user that is currently logged in with a session token.

## Post Endpoints

### Get all posts by user

`GET /api/users/<user_id>/posts/`

Response:

```json
{
  "posts": [<SERIALIZED POST>]
}
```

### Get all posts

`GET /api/posts/`

Response:

```json
{
    "posts": [
        {
            "id": 1,
            "title": "Found these AirPods",
            "image": <IMAGE URL (IF IMAGE WAS PROVIDED)>,
            "item": "AirPods",
            "status": "Lost",
            "text": "I found these yesterday - message me if they are yours!",
            "location": "Morrison Dining Hall",
            "timestamp": "2022-09-20 10:27:21.240752",
            "user_id": 1
        },
        ...
    ]
}
```

_Note:_

- Timestamp is a String representation of the DateTime object, and it is the time the post was created.

### Get post by id

`GET /api/posts/<post_id>/`

Response:

```json
{
    "id": <ID>,
    "title": <TITLE>,
    "image": <IMAGE URL (IF IMAGE WAS PROVIDED)>,
    "item" <ITEM>:,
    "status": <STATUS>,
    "text": <TEXT>,
    "location": <LOCATION>,
    "timestamp": <TIMESTAMP>,
    "user_id" <USER_ID>:
}
```

### Create post

`POST /api/posts/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Request:

```json
{
    "title": <USER INPUT>,
    "image": <USER INPUT (OPTIONAL - MUST BE BASE64 ENCODED)>,
    "item": <USER INPUT>,
    "status": <USER INPUT>,
    "text": <USER INPUT (OPTIONAL)>,
    "location": <USER INPUT>,
}
```

Response:

```json
{
    "id": <ID>,
    "title": <USER INPUT>,
    "image": <IMAGE URL OR NULL IF NOT PROVIDED>,
    "item": <USER INPUT>,
    "status": <USER INPUT>,
    "text": <USER INPUT OR NULL IF NOT PROVIDED>,
    "location": <USER INPUT>,
    "timestamp": <NOW>,
    "user_id": <USER_ID>
}
```

_Note:_

- Timestamp is the string representation of the DateTime object at the time the post is created.

### Edit post

`POST /api/posts/<post_id>/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Request:

```json
{
    "title": <USER INPUT (OPTIONAL)>,
    "image": <USER UNPUT (OPTIONAL - MUST BE BASE64 ENCODED)>,
    "item": <USER INPUT (OPTIONAL)>,
    "status": <USER INPUT (OPTIONAL)>,
    "text": <USER INPUT (OPTIONAL)>,
    "location": <USER INPUT (OPTIONAL)>,
}
```

Response:

```json
{
    "id": <ID>,
    "title": <USER INPUT OR PREVIOUS TITLE IF NOT PROVIDED>,
    "image": <IMAGE URL OR PREVIOUS IMAGE URL IF NOT PROVIDED>
    "item": <USER INPUT OR PREVIOUS ITEM IF NOT PROVIDED>,
    "status": <USER INPUT OR PREVIOUS STATUS IF NOT PROVIDED>,
    "text": <USER INPUT OR PREVIOUS TEXT IF NOT PROVIDED>,
    "location": <USER INPUT OR PREVIOUS LOCATION IF NOT PROVIDED>,
    "timestamp": <ORIGINAL TIMESTAMP>,
    "user_id": <USER_ID>
}
```

### Delete post

`DELETE /api/posts/<post_id>/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Response:

```json
{
    "id": <ID>,
    "title": <TITLE>,
    "image": <IMAGE URL>
    "item": <ITEM>,
    "status": <STATUS>,
    "text": <TEXT>,
    "location": <LOCATION>,
    "timestamp": <TIMESTAMP>,
    "user_id": <USER_ID>
}
```

## Conversation Endpoints

### Get all conversations by user

`GET /api/users/<user_id>/convos/`

Response:

```json
{
    "conversations": [
        {
            "id": <ID>,
            "user1_messages": [<SERIALIEZD MESSAGE>],
            "user2_messages": [<SERIALIZED MESSAGE>],
            "user1_id": <USER1_ID>,
            "user2_id": <USER2_ID>
        },
        ...
    ]
}
```

### Get conversation by id

`GET /api/users/<user_id>/convos/<conversation_id>/`

Response:

```json
{
    "id": <ID>,
    "user1_messages": [<SERIALIZED MESSAGE>],
    "user2_messages": [<SERIALIZED MESSAGE>],
    "user1_id": <USER1_ID>,
    "user2_id": <USER2_ID>
}
```

_Note:_

- User1_id is the ID of the user that first made the conversation
- User2_id is the ID of the user that <user_id> is messaging

### Create conversation

`POST /api/users/<user_id>/convos/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Request:

```json
{
    "username": <USER INPUT>
}
```

Response:

```json
{
    "id": <ID>,
    "user1_messages": [],
    "user2_messages": [],
    "user1_id": <user_id>,
    "user2_id": <ID OF USER INPUT>
}
```

### Delete conversation

`DELETE /api/users/<user_id>/convos/<conversation_id>/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Response:

```json
{
    "id": <conversation_id>,
    "user1_messages": [<SERIALIZED MESSAGE>],
    "user2_messages": [<SERIALIZED MESSAGE>],
    "user1_id": <USER1_ID>,
    "user2_id": <USER2_ID>
}
```

## Message Endpoints

### Send message

`POST /api/users/<user_id>/convos/<conversation_id>/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Request:

```json
{
    "receiver": <USER INPUT (USERNAME)>,
    "content": <USER INPUT>,
}
```

Response:

```json
{
    "id": <ID>,
    "sender_id": <user_id>,
    "receiver_id": <receiver_id>,
    "content": <USER INPUT>,
    "timestamp": <NOW>,
    "conversation_id": <conversation_id>
}
```

_Note:_

- Timestamp is the string representation of the DateTime object at the time the message is created.

### Get all messages

`GET /api/users/<user_id>/convos/<conversation_id>/messages/`

Response:

```json
{
    "messages": [
        {
            "id": <ID>,
            "sender_id": <SENDER_ID>,
            "receiver_id": <RECEIVER_ID>,
            "content": <CONTENT>,
            "timestamp": <NOW>,
            "conversation_id": <CONVERSATION_ID>
        },
        ...
    ]
}
```

### Get all messages from logged in user

`GET /api/users/<user_id>/convos/<conversation_id>/user/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Response:

```json
{
    "messages": [<SERIALIZED MESSAGE>]
}
```

### Get all messages from other user

`GET /api/users/<user_id>/convos/<conversation_id>/other/`

Request Header:
| Key | Value |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |

Response:

```json
{
    "messages": [<SERIALIZED MESSAGE>]
}
```
