# APP.PY functionality

## User App.Routes

### /users/getusers explaination
1. The @app.route decorator is used to define a new route in my Flask application:
`@app.route('/users/signup',`

2. The methods parameter specifies the HTTP methods that are allowed for this route. In this case, only the POST method is allowed:
`methods=['POST'])`

3.The add_user function is the view function that is called when a client sends a request to this route:
`def add_user():`

4.The function first checks if the request contains JSON data by inspecting the Content-Type header. If it is not set to application/json, the function returns an error response:
`if request.content_type != 'application/json':
    return jsonify("Error: Data must be json")`

5.The function then retrieves the username and password from the request body, which is assumed to be in JSON format:
`post_data= request.get_json()
username = post_data.get('username')
password = post_data.get('password')`

6.The function checks if a user with the same username already exists in the database. If so, it returns an error response:
`username_duplicate = db.session.query(User).filter(User.username == username).first()
if username_duplicate is not None:
    response = jsonify('Error: The username is already registered')
    return set_headers_post(response)`

7.If the username is not already taken, the function hashes the password using the bcrypt algorithm and creates a new user object with the provided username and hashed password:
`encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')
new_user = User(username, encrypted_password)`

8. The new user object is added to the database and the chages are commited:
`db.session.add(new_user)
db.session.commit()`

9. Finally, the function returns a success response with the details of the new user:
`response = jsonify(user_schema.dump(new_user))
return set_headers_post(response)`

### /users/login explaination

`@app.route('/users/login', methods=['POST'])
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

            return set_headers_post(response)`

This code defines an endpoint with the URL path "/users/login" that accepts HTTP POST requests. It checks if the request data is in JSON format and extracts the username and password from the request body. It then queries the database for a user with the provided username and checks if the password matches.

If the request contains a JWT token in the Authorization header, it tries to decode and validate the token. If the token is valid, it extracts the username from the token payload and queries the database for the corresponding user. If the user exists, it returns a response indicating that the user is already logged in, along with some additional information including the JWT token and whether the user is an admin.

If the request does not contain a valid JWT token, or if the token has expired, it checks if the username and password match a user in the database. If there is a match, it generates a new JWT token for the user, stores it in the response, and returns the user data along with some additional information.

The response is then wrapped with headers set by the set_headers_post function before it is returned to the client.

## Blog app routes

### /blog/getblogs explaination

1. This is a route for the GET HTTP method, with the endpoint '/blog/getblogs': 
`@app.route("/blog/getblogs", methods=['GET'])
def get_blogs():`

2. Query the database for all Blog objects and store them in the 'all_blogs' variable:
`all_blogs = Blog.query.all()`

3. Use the 'dump' method of the 'blog_schemas' object to serialize the 'all_blogs' variable into JSON format and store it in the 'result' variable: 
` result = blog_schemas.dump(all_blogs)`

4.Loop through all the blogs in the 'result' variable and sanitize their 'description' field using the 'clean' method of the 'bleach' module:
` for blog in result:
        blog['description'] = bleach.clean(blog['description'])`

5.Create a JSON response object containing the 'result' variable: 
`response = jsonify(result)`

6. Finally Return the JSON response object with the headers set by the 'set_header_get' function:
`return set_header_get(response)`

### /blog/postblog explaination