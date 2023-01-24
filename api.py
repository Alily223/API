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
    def __init__(self, username, password):
        self.username = username
        self.password = password

        
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
        
        new_user = User(username=username, password=password)

        db.session.add(new_user)
        db.session.commit()

        return user_schema.jsonify(new_user)

@app.route('/users/getusers', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)

    return jsonify(result)


@app.route('/users/login', methods=['POST'])
def login():
    username = request.json['name']
    password = request.json['password']

    admin_logged_in = False
    if username == 'AdminPrime' and password == 'AdminPassPrime':
        admin_logged_in = True
    

    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:
            return jsonify(success=True, message='User login successful', admin_logged_in=admin_logged_in), 200
        else:
            return jsonify(success=False, message='Incorrect password', admin_logged_in=admin_logged_in), 401
    else:
        return jsonify(success=False, message='User not found', admin_logged_in=admin_logged_in)

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
