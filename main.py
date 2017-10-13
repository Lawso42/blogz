from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blog@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'y33sp320sthp0882ped'
db = SQLAlchemy(app)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

#TODO rewrite index to update with Users.


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, blog_title, blog_body, owner):
        self.blog_title = blog_title
        self.blog_body = blog_body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref = 'owner')


    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'register_post', 'login_post']
    if request.endpoint in allowed_routes:
        pass
    else:
        if 'email' not in session:
            return redirect('/login')

@app.route('/', methods = ['POST', 'GET'])
def index():
    owner = User.query.filter_by(email=session['email']).first()
    #owner_name = Blog.query.filter_by(owner_id = session['owner_id']).first()
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        blog_post = Blog(blog_title, blog_body, owner)
        db.session.add(blog_post)
        db.session.commit()

    if request.args:
        blog_id = request.args.get("id")
        blog = Blog.query.get(blog_id)
        #blogs = Blog.query.filter_by(owner = owner).all()
        return render_template('blog-single.html', blog=blog)
    else:
        #blogs = ''
        blog_info = Blog.query.all()
        blogs = Blog.query.get("owner_id")
        owner_info = User.query.filter_by(id = blogs).first()
        
        #owner_number = Blog.query(owner)
        return render_template('Front-Page.html', title = "Build-a-Blog", blog_info = blog_info, blogs = blogs, owner_info = owner_info)



#TODO add user's posts to user's page
#TODO get user id, then get entries for that user in single-user.html

@app.route('/blog')
def user_list():
    user_id = Blog.query.get('owner_id')
    owner_id = User.query.get('id')
    user_names = Blog.query.all()
    user_info = User.query.all()
    if request.args:
    #if request.method == 'POST':
        blog_id = int(request.args.get("id"))
        user_id = request.args.get("owner_id")
        #user_id = User.query.get('id')
        user_names = Blog.query.all()
        user_info = User.query.all()
        user_name = User.query.get('id')
        user_more_names = Blog.query.get('owner_id')
        #blog_id = Blog.query.get('id')
        
        #blogs = Blog.query.filter_by(owner = owner).all()
        return render_template('single-user.html', user_name = user_name, user_names = user_names, blog_id = blog_id, user_more_names = user_more_names, owner_id = owner_id)
    
        
    
    return render_template('index.html', title = 'Users', user_info = user_info)


@app.route('/newpost', methods=['POST', 'GET'])
def new_blog():
    if request.method== 'GET':
        return render_template('blog-main.html', title="add blog entry")
    if request.method == 'POST':
        owner = User.query.filter_by(email=session['email']).first()
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ''
        body_error = ''
        if len(blog_title) < 1:
            title_error = "please fill in the title"
        if len(blog_body) < 1:
            body_error = "please fill in the body"
        if not title_error and not body_error:
            blog_post = Blog(blog_title, blog_body, owner)
            db.session.add(blog_post)
            db.session.commit()
            query_peram = '/?id=' + str(blog_post.id)
            return redirect(query_peram)
        else:
            return render_template('blog-main.html', title = 'add-blog', title_error = title_error, body_error = body_error, blog_title = blog_title, blog_body = blog_body)
    

@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html", title = "login")

@app.route('/login', methods=['POST'])
def login_post():
    email_error = ''
    password_error = ''
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if len(email) < 1:
        email_error = "please fill in the email"
    if len(password) < 1:
        password_error = "please fill in your password"
    if not user:
        email_error = 'this email is not in our records'
    if not email_error and not password_error:
        if user and user.password == password:
            session['email'] = email
            flash("Logged in", 'success')
            return redirect('/')
        else:
            return render_template("login.html", title = 'error', email_error = email_error, password_error = password_error, email = email, password = password)
            #flash('User password incorrect, or does not exist', 'error')
    else:
        password_error = 'invalid password'
        return render_template("login.html", title = 'error', email_error = email_error, password_error = password_error, email = email, password = password)
    return render_template("login.html", title = 'login')

@app.route('/register', methods =['GET'])
def register():
    return render_template("signup.html", title = 'register')


@app.route('/register', methods =['POST'])
def register_post():
    email = request.form['email']
    password = request.form['password']
    verify_password = request.form['verify']

    existing_user = User.query.filter_by(email=email).first()
    if existing_user == None:
        new_user = User(email, password)
        db.session.add(new_user)
        db.session.commit()
        flash("{} User Created".format(email), 'success')
        session['email'] = email
        return redirect('/')
    else:
        flash("User already exists.", 'error')
        return render_template('signup.html', title = 'register')
    return render_template('signup.html', title = 'register')

@app.route('/logout', methods=['GET'])
def logout():
    del session['email']
    return redirect('/')




if __name__ == '__main__':
    app.run()