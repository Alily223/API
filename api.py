import psycopg2
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate
from marshmallow.fields import Raw
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import Sequence, LargeBinary, Text, ForeignKey
from sqlalchemy.orm import relationship
from functools import wraps
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import bleach
import jwt
import base64
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Rascal9013123@localhost:5032/portfolioAPI'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bcrypt = Bcrypt(app)
CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Tables

class User(db.Model):
    user_id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
class Project(db.Model):
    project_id = db.Column(db.Integer, Sequence('project_id_seq'), primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(Text, nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)
    link = db.Column(Text, nullable=True)
    category = db.Column(db.String(100), nullable=False)
    testimonialprojectid = db.relationship('Testimonial', backref=db.backref('project',lazy=True), cascade='all, delete, delete-orphan')
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
    category = db.Column(db.String(200), nullable=False)
    def __init__(self, title, description, category):
        self.title = title
        self.description = description
        self.category = category
        
class HackerRank(db.Model):
    id = db.Column(db.Integer, Sequence('Hackerrank_id_seq'), primary_key=True)
    title = db.Column(db.String(200), unique=True, nullable=False)
    code = db.Column(Text, nullable=True)
    description = db.Column(Text, nullable=True)
    def __init__(self, title, code,description):
        self.title = title
        self.code = code
        self.description = description
        
class Testimonial(db.Model):
    id = db.Column(db.Integer, Sequence('Testimonials_id_seq'), primary_key=True)
    testimonial_title = db.Column(db.String(200), unique=True, nullable=False)
    testimonialprojectid = db.Column(db.Integer, ForeignKey('project.project_id') ,nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    review = db.Column(Text, nullable=True)
    def __init__(self,testimonial_title, testimonialprojectid, stars, review):
        self.testimonial_title = testimonial_title
        self.testimonialprojectid = testimonialprojectid
        self.stars = stars
        self.review = review
        

        
                
# Schemas

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
    
class BlogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blog

class UnfinishedProjSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UnfinishedProj
class CertificateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Certificate
        
class ProjectSchema(ma.SQLAlchemySchema):
    
    class Meta:
        model = Project
        
    project_id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String(required=True, validate=validate.Length(max=65535))
    image = Raw(required=False)
    link = fields.String(required=False, validate=validate.Length(max=65535))
    category = fields.String(required=True)
                
class TestimonialSchema(ma.SQLAlchemyAutoSchema):
    project_id = ma.Nested(ProjectSchema)
    testimonialprojectid = ma.auto_field()
    class Meta:
        model = Testimonial
        

user_schema = UserSchema()
users_schema = UserSchema(many=True)
        
blog_schema = BlogSchema()
blog_schemas = BlogSchema(many=True)
        
unfinishedProj_schema = UnfinishedProjSchema()
unfinishedProj_schemas = UnfinishedProjSchema(many=True)
       
certificate_schema = CertificateSchema()
certificates_schema = CertificateSchema(many=True)
        
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)

Testimonial_schema = TestimonialSchema()
Testimonial_schemas = TestimonialSchema(many=True)



def create_users_table():
    with app.app_context():
        db.create_all()
        
        
#middle-ware start

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]
            
        if not token:
            return {"message": "Token is missing"}, 401
        
        try: 
            data = jwt.decode(token, Config)
        except: 
            return {"message": "Token is inavlid"}, 401
        
        return f(*args, **kwargs)
    return decorated

def set_headers_post(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'POST')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

def set_headers_put(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'PUT')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

def set_header_delete(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'DELETE')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response
    

#middle-ware start

#User app routes -------------------------------------------------------------------------------

@app.route('/users/signup', methods=['POST'])
def add_user():
    if request.content_type != 'application/json':
        return jsonify("Error: Data must be json")
    # Get the username and password from the request body
    post_data= request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')

    # Check if a user with the same username already exists
    username_duplicate = db.session.query(User).filter(User.username == username).first()
    
    if username_duplicate is not None:
        response = jsonify('Error: The username is already registered')
        return set_headers_post(response)
    
    encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username, encrypted_password)
    
    db.session.add(new_user)
    db.session.commit()
    
    response = jsonify(user_schema.dump(new_user))
    return set_headers_post(response)

@app.route('/users/getusers', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)

    return jsonify(result)


@app.route('/users/login', methods=['POST'])
def login():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Data must be json'})
    
    post_data = request.get_json()
    username = post_data.get('username')
    password = post_data.get('password')
    user = db.session.query(User).filter(User.username == username).first()
    
    print("the token with Bearer :" , request.headers.get('Authorization'))

    if request.headers.get('Authorization') != "Bearer null":
        try:
            token = request.headers.get('Authorization').split(' ')[1]
            print("then token without bearer:", token)
            secret = app.config["SECRET_KEY"]
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            print("the payload:", payload)
            username = payload["username"]
            print("username from payload:", username)
            user = db.session.query(User).filter(User.username == username).first()
            if user:
                print("if user route")
                admin_logged_in = False
                if username == 'AustinLily' and password == "Rascal":
                    admin_logged_in = True
                response = jsonify({'message': 'User already logged in', 'data': payload, 'admin_logged_in': admin_logged_in,'user_found': True})
                return set_headers_post(response)
            else:
                response = jsonify({"error: ahhhh help me"})
                return set_headers_post(response)
        except jwt.ExpiredSignatureError:
            response = jsonify({'error': 'Token has expired'})
            return set_headers_post(response)
        except jwt.InvalidTokenError:
            if user is None:
                response = jsonify({'error': 'user NONE EXISTENT'})
                return set_headers_post(response)
            elif not bcrypt.check_password_hash(user.password, password):
                response = jsonify({'error': 'PASSWORD WRONG TRY AGAIN'})
                return set_headers_post(response)
            else:
                print("InavlidTokenError route")
                admin_logged_in = False
                if username == 'AustinLily' and password == "Rascal":
                    admin_logged_in = True
        
                    payload = {
                        "username": username
                    }
        
                    secret = app.config["SECRET_KEY"]
                    token = jwt.encode(payload, secret, algorithm="HS256")

                    response = jsonify({'token': token,
                                        'data': user_schema.dump(user),
                                        'admin_logged_in': admin_logged_in,
                                        'user_found': True})
        
                    return set_headers_post(response)
    elif request.headers.get('Authorization') == "Bearer null":
        print("elif bearer is null so go to line 263")
        if user is None:
                response = jsonify({'error': 'user NONE EXISTENT'})
                return set_headers_post(response)
        elif not bcrypt.check_password_hash(user.password, password):
                response = jsonify({'error': 'PASSWORD WRONG TRY AGAIN'})
                return set_headers_post(response)
        else:
            admin_logged_in = False
            if username == 'AustinLily' and password == "Rascal":
                admin_logged_in = True
    
            payload = {
                "username": username
            }
    
            secret = app.config["SECRET_KEY"]
            token = jwt.encode(payload, secret, algorithm="HS256")

            response = jsonify({'token': token,
                                'data': user_schema.dump(user),
                                'admin_logged_in': admin_logged_in,
                                'user_found': True})

            return set_headers_post(response)

        

        

#Blog app routes------------------------------------------------------------------------------

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
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be json')
    
    post_data = request.get_json()
    title = post_data.get('name')
    description = post_data.get('description')
    category = post_data.get('category')
    
    blog_duplicate = db.session.query(Blog).filter(Blog.title == title).first()
    
    if blog_duplicate is not None: 
        response = jsonify("Blog already exists")
        return set_headers_post(response)
    
    new_blog = Blog(title=title, description=description, category=category)
    
    db.session.add(new_blog)
    db.session.commit()
    
    response = jsonify(blog_schema.dump(new_blog))
    return set_headers_post(response)
    
@app.route("/blog/<int:blog_id>", methods=['DELETE'])
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    response = jsonify({'message': 'Blog deleted successfully'})
    return set_header_delete(response)

@app.route("/updateblog/<int:blog_id>", methods=["POST"])
def edit_blog(blog_id):
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be json')
    
    post_data = request.get_json()
    description = post_data.get('description')
    
    if description == "":
        print(description)
        response = jsonify({'error': 'Description is null'})
        return set_headers_post(response)
    
    blog = db.session.query(Blog).filter(Blog.id == blog_id).first()
    
    if blog:
        blog.description = description
        db.session.commit()
        
        response = jsonify(blog_schema.dump(blog))
        return set_headers_post(response)
    else:
        response = jsonify({'error': 'Blog not found'})
        return set_headers_post(response)
    
        
# project app routes ------------------------------------------------------------------

@app.route("/project/Add", methods=["POST"])
def project_add():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be json')
    
    post_data = request.get_json()
    title = post_data.get('name')
    link = post_data.get('link')
    category = post_data.get('category')
    image = post_data.get('image')
    description = post_data.get('description')
    
    if image is not None:
        image_data = bytes(image)
        image_str = base64.b64encode(image_data).decode('utf-8')
        image_bytes = image_str.encode('utf-8')
    else:
        image = None 
        image_str = None
        image_bytes = None
    
    # print(image)
    # print(image_bytes)
    
    project_duplicate = db.session.query(Project).filter(Project.title == title).first()
    
    if project_duplicate is not None: 
        response = jsonify("Project already exists")
        return set_headers_post(response)
    
    new_project = Project(title=title, description=description, image=image_bytes, link=link, category=category)
    
    db.session.add(new_project)
    db.session.commit()
    
    response = jsonify(project_schema.dump(new_project))
    return set_headers_post(response)

@app.route("/project/GetAll", methods=["GET"])
def project_getall():
    all_projects = Project.query.all()
    result = projects_schema.dump(all_projects)
    
    for project in result: 
        project['description'] = bleach.clean(project['description'])
        
    return jsonify(result)

@app.route("/projectsupdate/<int:project_id>", methods=["POST"])
def project_update(project_id):
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be json')
    
    post_data = request.get_json()
    title = post_data.get('name')
    link = post_data.get('link')
    category = post_data.get('category')
    image = post_data.get('image')
    # print(image)
    description = post_data.get('description')
    
    if image is not None:
        image_data = bytes(image)
        image_str = base64.b64encode(image_data).decode('utf-8')
        image_bytes = image_str.encode('utf-8')
    else:
        image = None 
        image_str = None
        image_bytes = None
    
    project = db.session.query(Project).filter(Project.id == project_id).first()
    
    if project:
        project.title = title
        project.description = description
        project.image = image_bytes
        project.link = link
        project.category = category
        db.session.commit()
        
        response = jsonify(project_schema.dump(project))
        return set_headers_post(response)
    else:
        response = jsonify({"Error": "Project Non Existent"})
        return set_headers_post(response)

@app.route('/project/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    response = jsonify({'message': 'Project deleted successfully'})
    return set_header_delete(response)

if __name__ == '__main__':
    create_users_table()
    app.run(debug=True)