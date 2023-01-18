import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Sequence

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ijyulyynvgiiwv:474e7a9f51a81d99df57c936d81eed1864bf9f2e9a8d826bc008b52467022267@ec2-54-160-109-68.compute-1.amazonaws.com:5432/dchc82g7i6qkv1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)

db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, Sequence('user_id_seq'), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

user_schema = UserSchema()
users_schema = UserSchema(many=True)

def create_users_table():
    with app.app_context():
        db.create_all()


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

@app.route('/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)

    return jsonify(result)

@app.route('/users/login', methods=['POST'])
def login():
    username = request.json['name']
    password = request.json['password']
    
    if username == 'AdminPrime' and password == 'AdminPassPrime':
        admin_logged_in = True
    else:
        admin_logged_in = False

    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:
            return jsonify({'message': 'Successfully logged in.', 'admin_logged_in': admin_logged_in}), 200
        else:
            return jsonify({'message': 'Invalid password.'}), 401
    else:
        return jsonify({'message': 'Invalid username.'}), 401

if __name__ == '__main__':
    create_users_table()
    app.run(debug=True)
