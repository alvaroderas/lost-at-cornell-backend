import datetime, hashlib, os, base64, boto3, io, random, re, string, bcrypt
from flask_sqlalchemy import SQLAlchemy
from mimetypes import guess_extension, guess_type
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpg", "jpeg"]
BASE_DIR = os.getcwd()
load_dotenv()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-2.amazonaws.com"

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
    pfp_id = db.Column(db.Integer, db.ForeignKey("asset.id"), nullable=True)
    pfp = db.relationship("Asset", cascade="delete")

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
        pfp_url = None
        if self.pfp is not None:
            pfp_url = self.pfp.serialize()["url"]
        
        if self.pfp is None:
            return {
                "id": self.id,
                "name": self.name,
                "username": self.username,
                "email": self.email,
                "posts": [p.serialize() for p in self.posts],
                "conversations": [c.serialize() for c in self.conversations]
            }
        else:
            return {
                "id": self.id,
                "name": self.name,
                "username": self.username,
                "email": self.email,
                "pfp": pfp_url,
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
    image = db.relationship("Asset", cascade="delete")
    image_id = db.Column(db.Integer, db.ForeignKey("asset.id"), nullable=True)
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
        image_url = None
        if self.image is not None:
            image_url = self.image.serialize()["url"]
            
        if self.image is None:
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
        else:
            return {
                "id": self.id,
                "title": self.title,
                "image": image_url,
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
    
    
class Asset(db.Model):
    """
    Asset model
    """
    __tablename__ = "asset"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_url = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        """
        Initializes an Asset Object
        """
        self.create(kwargs.get("image_data"))

    def serialize(self):
        """
        Serializes an Asset Object
        """
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at)
        }

    def create(self, image_data):
        """
        Given an image in base64 encoding, does the following:
        1. Rejects the image if it is not a supported filename
        2. Generate a random String for the image filename
        3. Decodes the image and attempts to upload it to aws
        """
        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]
            if ext not in EXTENSIONS:
                raise Exception(f"Extension {ext} is not valid!")
            
            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)
            )

            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data = base64.b64decode(img_str)
            img =Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datetime.datetime.now()

            img_filename = f"{self.salt}.{self.extension}"

            self.upload(img, img_filename)


        except Exception as e:
            print(f"Error when creating image: {e}")

    def upload(self, img, img_filename):
        """
        Attempts to upload the image into the specified S3 bucket
        """
        try:
            #save image into temporary
            img_temp_loc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temp_loc)
            
            #upload img into S3 bucket
            s3_client = boto3.client("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            s3_client.upload_file(img_temp_loc, S3_BUCKET_NAME, img_filename)

            s3_resource = boto3.resource("s3", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
            object_acl.put(ACL = "public-read")
            #remove img from temp location
            os.remove(img_temp_loc)


        except Exception as e:
            print(f"Error when uploading image: {e}")
