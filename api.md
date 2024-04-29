# API Specification

Values wrapped in `< >` are placeholders for what the field values should be. Also be sure to read the request route carefully when you implement it.

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
    "posts": [<SERIALIZED POST>],
    "conversations": [<SERIALIZED CONVERSATION>]
}
```

### Edit user information

`POST /api/users/edit/`

Request:

```json
{
    "name": <USER INPUT (OPTIONAL)>,
    "username": <USER INPUT (OPTIONAL)>,
    "email": <USER INPUT (OPTIONAL)>,
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
    "posts": [<SERIALIZED POST>],
    "conversations": [<SERIALIZED CONVERSATION>]
}
```

_Note:_

- The edit user endpoint works by editing the user that is currently logged in with a session token.

### Delete user

`DELETE /api/users/delete/`

Response:

```json
{
    "id": <ID>,
    "name": <NAME> ,
    "username": <USERNAME>,
    "email": <EMAIL>,
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

Response:
