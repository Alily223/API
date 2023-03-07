# APP.PY functionality
backend for portfolio site
front end located at https://lilygrenportfolio.herokuapp.com/
the backend can be located at https://backendforlilygrenportfolio.herokuapp.com/
## App.Routes Explaination

### User Creation
A user can create a username and password to be stored
> Endpoint: '/users/signup', Method:'POST'
Expected Response:
    `{
        "userid": INT,
        "username": STR,
        "password": STR
    }`

### Blog Creation
A admin can post a blog to be stored
> Endpoint: `blog/postblog` , Method:'POST'
Expected Response:
    `{
        "id": INT,
        "title": STR,
        "description":STR,
        "category":STR
    }`

### Admin Project Creation
A admin can post a project to be stored
> Endpoint: `project/Add`, Method: 'POST'
Expected Response:
    `{
        "project_id": INT,
        "title": STR,
        "description": STR,
        "image": STR,
        "link": STR,
        "category": STR
    }`

### Admin Project Adapatation
A admin can grab the project to be edited via POST
> Endpoint: '/projectsupdate/int:project_id_sent', Method="POST"
Expected Response:
    `{
        "project_id": INT,
        "title": STR,
        "description": STR,
        "image": STR,
        "link": STR,
        "category": STR
    }`

### Admin Testimonial Creation
A admin can create a testimonial for a user to grab the testimonial by code and or the user can create a testimonial by project selection
> Endpoint: '/testimonialunpblished/add', Method="POST"
Expected Response:
    `{
        'id': INT,
        'testimonial_title': STR, 
        'testimonialprojectid': INT, 
        'stars': INT, 
        'review': STR, 
        'testimonial_username': STR, 
        'twelvedigitcode': STR
    }`

### Admin Testimonial Adaptation
A admin can grab a testimonial by id and edit it then send the data via POST
> Endpoint: '/testimonialpublished/grabforedit/int:testimonial_id' , Method="POST"
Expected Response:
    `{
        'id': INT,
        'testimonial_title': STR, 
        'testimonialprojectid': INT, 
        'stars': INT, 
        'review': STR, 
        'testimonial_username': STR, 
        'twelvedigitcode': STR
    }`

### Admin Testimonial Publish
A admin can send a testimonial to be published to the published testimonial table
> Endpoint: '/sendtopublishedtestimonials/add' , Method="POST"
Expected Response:
    `{
        "id": INT, 
        'publishedtitle':STR,
        'publishedprojectid':INT,
        'stars':INT,
        'review':STR,
        'testimonial_username':STR,
        'twelvedigitcode':STR
    }`

### User Get All
The frontend grabs all users
> Endpoint: '/users/getusers' , Method="GET"
Expected Response:
    `{
        "id": INT,
        "title": STR,
        "description":STR,
        "category":STR
    }`

### Blog Get All
The frontend grabs all blogs
> Endpoint: '/blog/getblogs' , Method="GET"
Expected Response:
    `{
        "id": INT,
        "title": STR,
        "description":STR,
        "category":STR
    }`

### Project Get All
The frontend grabs all projects
> Endpoint: '/project/GetAll' , Method="GET"
Expected Response:
    `{
        "project_id": INT,
        "title": STR,
        "description": STR,
        "image": STR,
        "link": STR,
        "category": STR
    }`

### Testimonial Get All
the frontend grabs all testimonials for Admin
> Endpoint: '/testimonialunpublished/getall' , Method="GET"
Expected Response:
    `{
        'id': INT,
        'testimonial_title': STR, 
        'testimonialprojectid': INT, 
        'stars': INT, 
        'review': STR, 
        'testimonial_username': STR, 
        'twelvedigitcode': STR
    }`

### Testimonial Single Get
the user grabs a Testimonial by its twelvedigit code
> Endpoint: '/testimonialpublished/grabforuser/string:testimonial_code' , Method="GET"
Expected Response:
    `{
        'id': INT,
        'testimonial_title': STR, 
        'testimonialprojectid': INT, 
        'stars': INT, 
        'review': STR, 
        'testimonial_username': STR, 
        'twelvedigitcode': STR
    }`

### Published Testimonial Get All
the frontend grabs all testimonials
> Endpoint: '/truepublishedtestimonials/getall' , Method="GET"
Expected Response:
    `{
        "id": INT, 
        'publishedtitle':STR,
        'publishedprojectid':INT,
        'stars':INT,
        'review':STR,
        'testimonial_username':STR,
        'twelvedigitcode':STR
    }`

### Blog Deletion
The Admin Deletes a blog by id
> Endpoint: '/blog/int:blog_id', Method="DELETE"
Expected Response:
    '{
        'message': Blog deleted successfully
    }'

### Project Deletion
The Admin Deletes a project by id
> Endpoint: '/project/int:project_id', Method="DELETE"
Expected Response:
    '{
        'message': Project deleted successfully
    }'

### Testimonial Deletion
The Admin Deletes a testimonial by id
> Endpoint: '/testimonialunpublished/delete/int:testimonial_id', Method="DELETE"
Expected Response:
    '{
        'message': Testimonial deleted successfully
    }'
### Published Testimonial Deletion
The admin deletes a published testiominal
> Endpoint: '/truepublishedtestimonials/int:testimonial_id', Method="DELETE"
Expected Response:
    '{
        'message': PublishedTestimonial deleted successfully
    }'