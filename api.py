import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Sequence, LargeBinary, Text, ForeignKey
from sqlalchemy.orm import relationship
from functools import wraps
import bleach
import jwt
from config import secret, adminsecret
import bcrypt

import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Rascal9013123@localhost:5032/portfolioAPI'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Tables
class User(db.Model):
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    salt = db.Column(db.String(200), nullable=False)
    def __init__(self, username, password):
        self.username = username
        self.salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, self.salt)
        self.password = hashed_password

        
class Project(db.Model):
    id = db.Column(db.Integer, Sequence('project_id_seq'), primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(Text, nullable=True)
    image = db.Column(LargeBinary, nullable=True)
    link = db.Column(Text, nullable=True)
    category = db.Column(db.String(100), nullable=False)
    def __init__(self, title, description, image, link, category):
        self.title = title
        self.description = description
        self.image = image
        self.link = link
        self.category = category 
    
class Certificate(db.Model):
    id = db.Column(db.Integer, Sequence('Certificate_id_seq'), primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(Text, nullable=True)
    image = db.Column(LargeBinary, nullable=True)
    def __init__(self, title, description, image):
        self.title = title
        self.description = description 
        self.image = image
   

class UnfinishedProj(db.Model):
    id = db.Column(db.Integer, Sequence('UnfinishedProj_id_seq'), primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(Text, nullable=True)
    progress = db.Column(db.Integer, nullable=True)
    def __init__(self, title, description, progress):
        self.title = title
        self.description = description
        self.progress = progress
        
class Blog(db.Model):
    id = db.Column(db.Integer, Sequence('Blog_id_seq'), primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(Text, nullable=True)
    def __init__(self, title, description):
        self.title = title
        self.description = description
       
    
        
# Schemas
class BlogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blog

class UnfinishedProjSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UnfinishedProj
class CertificateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Certificate
        
class ProjectSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        
blog_schema = BlogSchema()
blog_schemas = BlogSchema(many=True)
        
unfinishedProj_schema = UnfinishedProjSchema()
unfinishedProj_schemas = UnfinishedProjSchema(many=True)
       
certificate_schema = CertificateSchema()
certificates_schema = CertificateSchema(many=True)
        
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

def create_users_table():
    with app.app_context():
        db.create_all()
        
        
#middle-ware start

def validate_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            payload = jwt.decode(token, secret if payload["role"] != "admin" else adminsecret)
            if payload["role"] != "admin":
                return jsonify({'error': 'Not authorized'}), 401
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return jsonify({'error': 'Token is invalid'}), 401
        response.headers.add('Access-Control-Allow-Origin', '*')
        return f(*args, **kwargs)
    return decorated_function


#middle-ware start

#User app routes 

@app.route('/users/signup', methods=['POST'])
def add_user():
    # Get the username and password from the request body
    username = request.json.get('name')
    password = request.json.get('password')

    # Check if a user with the same username already exists
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({'userinsertmessage':'user cant create'}), 409 
    else:
        # Hash the password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return user_schema.jsonify(new_user)

@app.route('/users/getusers', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)

    return jsonify(result)

@validate_token
@app.route('/users/login', methods=['POST'])
def login():
    token = request.headers.get('Authorization')
    if token:
        try:
            payload = jwt.decode(token, secret if payload.get("role") != "admin" else adminsecret if payload else secret)
            if payload['username'] and payload['user_id']:
                response = jsonify({'message': 'Successfully logged in.', 'userLogInStatus': 'LOGGED_IN'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            pass

    # If the token is missing or invalid, continue with the login process
    username = request.json['name']
    password = request.json['password']

    admin_logged_in = False
    if username == 'AdminPrime' and password == 'AdminPassPrime':
        admin_logged_in = True

    user = User.query.filter_by(username=username).first()
    if user:
        print("output",str(password.encode()))
        if bcrypt.checkpw(password.encode(), user.password.encode(), user.salt.encode()):
            payload = {'user_id': user.id, 'admin': admin_logged_in, 'username':username}
            token = jwt.encode(payload, secret if not admin_logged_in else adminsecret)
            if token is None:
                return jsonify({'error': 'Error generating token'}), 500
            else:
                response = jsonify({'message': 'Successfully logged in.', 'admin_logged_in': admin_logged_in, 'token': token, 'userLogInStatus': 'LOGGED_IN'})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
        else:
            response = jsonify({'message': 'Invalid password.', 'userLogInStatus': 'NOT_LOGGED_IN'})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 401
    else:
        response = jsonify({'message': 'Invalid username.', 'userLogInStatus': 'NOT_LOGGED_IN'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 401
    response = jsonify({'message': 'Unauthorized access.', 'userLogInStatus': 'NOT_LOGGED_IN'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response, 401

#Blog app routes

@app.route("/blog/getblogs", methods=['GET'])
def get_blogs():
    all_blogs = Blog.query.all()
    result = blog_schemas.dump(all_blogs)
    # Iterate over the blogs and sanitize the 'description' field
    for blog in result:
        # Sanitize the text and set it as the 'description' field
        blog['description'] = bleach.clean(blog['description'])
    return jsonify(result)

@app.route("/blog/postblog", methods=['POST'])
def post_blog():
    title = request.json.get('name')
    description = request.json.get('description')
    new_blog = Blog(title=title, description=description)
    db.session.add(new_blog)
    db.session.commit()
    return jsonify(new_blog)



@app.route("/blog/<int:blog_id>", methods=['DELETE'])
def delete_blog(blog_id):
    blog = Blog.query.get(blog_id)
    db.session.delete(blog)
    db.session.commit()
    return 'Blog post deleted', 204

if __name__ == '__main__':
    create_users_table()
    app.run(debug=True)
