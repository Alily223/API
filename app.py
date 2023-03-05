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

app = Flask(__name__)

load_dotenv()

database_grab = os.getenv('DATABASE_URL')


app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://qziilkqfnrhknl:308cf4d03d0fb15dbea72dab9675e9d49c3df0f1d0967ee12a74a06b98174eb8@ec2-52-54-212-232.compute-1.amazonaws.com:5432/dedml2sbeql541'
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
    image = db.Column(Text, nullable=True)
    link = db.Column(Text, nullable=True)
    category = db.Column(db.String(100), nullable=False)
    testimonialprojectid = db.relationship('Testimonial', backref=db.backref('project',lazy=True), cascade='all, delete, delete-orphan')
    publishedprojectid = db.relationship('Publishedtestimonial',  backref=db.backref('project',lazy=True), cascade='all, delete, delete-orphan')
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
    image = db.Column(Text, nullable=True)
    def __init__(self, title, description, image):
        self.title = title
        self.description = description 
        self.image = image
        
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
    testimonial_username = db.Column(db.String(200), nullable=False)
    twelvedigitcode = db.Column(db.String(14), unique=True, nullable=False)
    def __init__(self,testimonial_title, testimonialprojectid, stars, review, testimonial_username, twelvedigitcode):
        self.testimonial_title = testimonial_title
        self.testimonialprojectid = testimonialprojectid
        self.stars = stars
        self.review = review
        self.testimonial_username = testimonial_username
        self.twelvedigitcode = twelvedigitcode
        
class Publishedtestimonial(db.Model):
    id = db.Column(db.Integer, Sequence('Testimonials_id_seq'), primary_key=True)
    publishedtitle = db.Column(db.String(200), unique=True, nullable=False)
    publishedprojectid = db.Column(db.Integer, ForeignKey('project.project_id') ,nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    review = db.Column(Text, nullable=True)
    testimonial_username = db.Column(db.String(200), nullable=False)
    twelvedigitcode = db.Column(db.String(14), unique=True, nullable=False)
    def __init__(self,publishedtitle, publishedprojectid, stars, review, testimonial_username, twelvedigitcode):
        self.publishedtitle = publishedtitle
        self.publishedprojectid = publishedprojectid
        self.stars = stars
        self.review = review
        self.testimonial_username = testimonial_username
        self.twelvedigitcode = twelvedigitcode
        
                
# Schemas

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
    
class BlogSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blog
class CertificateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Certificate
        
class ProjectSchema(ma.SQLAlchemySchema):
    
    class Meta:
        model = Project
        
    project_id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    description = fields.String(required=True, validate=validate.Length(max=65535))
    image = fields.String(required=False)
    link = fields.String(required=False, validate=validate.Length(max=65535))
    category = fields.String(required=True)
                
class TestimonialSchema(ma.SQLAlchemyAutoSchema):
    project_id = ma.Nested(ProjectSchema)
    testimonialprojectid = ma.auto_field()
    class Meta:
        model = Testimonial
        
class PublishedtestimonialSchema(ma.SQLAlchemyAutoSchema):
    project_id = ma.Nested(ProjectSchema)
    publishedprojectid = ma.auto_field()
    class Meta:
        model = Publishedtestimonial

user_schema = UserSchema()
users_schema = UserSchema(many=True)
        
blog_schema = BlogSchema()
blog_schemas = BlogSchema(many=True)
    
certificate_schema = CertificateSchema()
certificates_schema = CertificateSchema(many=True)
        
project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)

Testimonial_schema = TestimonialSchema()
Testimonial_schemas = TestimonialSchema(many=True)

Publishedtestimonial_schema = PublishedtestimonialSchema()
Publishedtestimonial_schemas = PublishedtestimonialSchema(many=True)


# def create_users_table():
#     with app.app_context():
#         db.create_all()
        
        
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

def set_header_get(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
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

    response = jsonify(result)
    return set_header_get(response)


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
        
    response = jsonify(result)
    return set_header_get(response)

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
    #print(image)
    
    if image is not None:
        image_data = bytes(image)
        #print(image_data)
        image_str = base64.b64encode(image_data).decode('utf-8')
    else:
        image = None 
        image_str = None
        
    dict_for_image_bytes = {'ImageBytes': image_str}
    json_for_image = json.dumps(dict_for_image_bytes)
    #print(dict_for_image_bytes)
    
    
    #print(len(image_bytes))
    
    project_duplicate = db.session.query(Project).filter(Project.title == title).first()
    
    if project_duplicate is not None: 
        response = jsonify("Project already exists")
        return set_headers_post(response)
    
    new_project = Project(title=title, description=description, image=json_for_image, link=link, category=category)
    
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
    
    response = jsonify(result)
    return set_header_get(response)

@app.route("/projectsupdate/<int:project_id_sent>", methods=["POST"])
def project_update(project_id_sent):
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
        #print(image_data)
        image_str = base64.b64encode(image_data).decode('utf-8')
    else:
        image_data = bytes(image)
        #print(image_data)
        image_str = base64.b64encode(image_data).decode('utf-8')
        
    dict_for_image_bytes = {'ImageBytes': image_str}
    json_for_image = json.dumps(dict_for_image_bytes)
    
    project = db.session.query(Project).filter(Project.project_id == project_id_sent).first()
    
    if project:
        project.title = title
        project.description = description
        project.image = json_for_image
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

# testimonial / published testimonial app routes ------------------------------------------------------------------

@app.route('/testimonialunpblished/add', methods=['POST'])
def testiomonialAdd():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be json')
    
    post_data = request.get_json()
    title = post_data.get('title')
    projectid = post_data.get('pid')
    stars = post_data.get('stars')
    username = post_data.get('username')
    twelvedigcode = post_data.get('code')
    description = post_data.get('description')
    
    testimonial_duplicate = db.session.query(Testimonial).filter(Testimonial.testimonial_title == title).first()
    code_duplicate = db.session.query(Testimonial).filter(Testimonial.twelvedigitcode == twelvedigcode).first()
    
    if testimonial_duplicate is not None:
        response = jsonify("Testimonial already exists")
        return set_headers_post(response)
    
    if code_duplicate is not None:
        response = jsonify("Twelve Digit Code already exists")
        return set_headers_post(response)
    
    new_testimonial = Testimonial(testimonial_title=title, testimonialprojectid=projectid, stars=stars, review=description, testimonial_username=username, twelvedigitcode=twelvedigcode)
    
    db.session.add(new_testimonial)
    db.session.commit()
    
    response = jsonify(Testimonial_schema.dump(new_testimonial))
    return set_headers_post(response)

@app.route('/testimonialunpublished/getall', methods=['GET'])
def testimonialgetall():
    all_testimonials = Testimonial.query.all()
    result = Testimonial_schemas.dump(all_testimonials)
    
    for testimonial in result:
        testimonial['review'] = bleach.clean(testimonial['review'])
    
    response = jsonify(result)
    return set_header_get(response)

@app.route('/testimonialunpublished/delete/<int:testimonial_id>', methods=['DELETE'])
def testimonialdelete(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()
    response = jsonify({'message': 'Testimonial deleted successfully'})
    return set_header_delete(response)
    
@app.route('/testimonialpublished/grabforedit/<int:testimonial_id>', methods=['POST'])
def testimonialedit(testimonial_id):
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be json')
    
    post_data = request.get_json()
    title = post_data.get('title')
    projectid = post_data.get('pid')
    stars = post_data.get('stars')
    username = post_data.get('username')
    description = post_data.get('description')
    
    testimonial = db.session.query(Testimonial).filter(Testimonial.id == testimonial_id).first()
    
    # print(testimonial)
    
    if testimonial:
        testimonial.testimonial_title = title
        testimonial.testimonialprojectid = projectid
        testimonial.stars = stars
        testimonial.review = description
        testimonial.testimonial_username = username
        db.session.commit()
        
        response = jsonify(Testimonial_schema.dump(testimonial))
        # print(response)
        return set_headers_post(response)
    else:
        response = jsonify({"Error": "Testimonial Non Existent"})
        # print(response)
        return set_headers_post(response)
        
        
@app.route('/testimonialpublished/grabforuser/<string:testimonial_code>', methods=['GET']) 
def grabTestimonialByReferredCode(testimonial_code):
    testimonial = Testimonial.query.filter_by(twelvedigitcode=testimonial_code).first()
    
    if not testimonial:
        return jsonify({'message': 'Testimonial not found.'})
    
    result = Testimonial_schema.dump(testimonial)
    
    response = result
    
    return set_header_get(response)

@app.route('/sendtopublishedtestimonials/add', methods=['POST'])
def sendtopublishedtestimonials():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be json')
    
    post_data = request.get_json()
    title = post_data.get('title')
    projectid = post_data.get('pid')
    stars = post_data.get('stars')
    username = post_data.get('username')
    twelvedigcode = post_data.get('code')
    description = post_data.get('description')
    
    testimonial_duplicate = db.session.query(Publishedtestimonial).filter(Publishedtestimonial.publishedtitle == title).first()
    
    if testimonial_duplicate is not None:
        response = jsonify("Testimonial already exists")
        return set_headers_post(response)
    
    new_published_testimonial = Publishedtestimonial(publishedtitle=title, publishedprojectid=projectid, stars=stars, review=description, testimonial_username=username, twelvedigitcode=twelvedigcode)
    
    db.session.add(new_published_testimonial)
    db.session.commit()
    
    response = jsonify(Publishedtestimonial_schema.dump(new_published_testimonial))
    return set_headers_post(response)

@app.route('/truepublishedtestimonials/getall', methods=['GET'])
def getallpublishedtestimonials():
    all_published_testimonials = Publishedtestimonial.query.all()
    result = Publishedtestimonial_schemas.dump(all_published_testimonials)
    
    for testimonial in result:
        testimonial['review'] = bleach.clean(testimonial['review'])
    
    response = jsonify(result)
    return set_header_get(response)

@app.route('/truepublishedtestimonials/<int:testimonial_id>', methods=['DELETE'])
def deletepublishedtestimonial(testimonial_id):
    published_testimonial = Publishedtestimonial.query.get_or_404(testimonial_id)
    db.session.delete(published_testimonial)
    db.session.commit()
    response = jsonify({'message': 'Testimonial deleted successfully'})
    return set_header_delete(response)
        
    
if __name__ == '__main__':
    app.run(debug=True)