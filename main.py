from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
import os
import jinja2
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.String(1000))


    def __init__(self, blog_title, blog_body):
        self.blog_title = blog_title
        self.blog_body = blog_body



@app.route('/newblog', methods = ['GET'])
def index():
    if request.args:
        blog_id = request.args.get("id")
        blog = Blog.query.get(blog_id)
        return render_template('blog-single.html', blog=blog)
    else:
        blog_info = Blog.query.all()
        return render_template('Front-Page.html', title = "Build-a-Blog", blog_info = blog_info)


@app.route('/newpost', methods=['POST', 'GET'])
def new_blog():
    if request.method== 'GET':
        return render_template('blog-main.html', title="add blog entry")
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        title_error = ''
        body_error = ''
        if len(blog_title) < 1:
            title_error = "please fill in the title"
        if len(blog_body) < 1:
            body_error = "please fill in the body"
        if not title_error and not body_error:
            blog_post = Blog(blog_title, blog_body)
            db.session.add(blog_post)
            db.session.commit()
            query_peram = '/newblog?id=' + str(blog_post.id)
            return redirect(query_peram)
        else:
            return render_template('blog-main.html', title = 'add-blog', title_error = title_error, body_error = body_error, blog_title = blog_title, blog_body = blog_body)
    




if __name__ == '__main__':
    app.run()