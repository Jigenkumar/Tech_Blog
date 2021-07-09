from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
import os
from werkzeug.utils import secure_filename

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app = Flask(__name__)
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD = params['gmail-password']
)
mail = Mail(app)

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['Local_url']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_url']

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['UPLOAD_FOLDER'] = params['upload_file']
app.secret_key = 'super-secret-key'

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    message = db.Column(db.String(180), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    date_time = db.Column(db.String(12),nullable=False)

class blog(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    sub_heading = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(180), nullable=False)
    name = db.Column(db.String(12), nullable=False)
    img_file = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12),nullable=False)
    
@app.route("/")
def home():
    post = blog.query.filter_by().all()[0:5]
    return render_template('index.html',params=params, post=post)

@app.route("/about",)
def about():
    return render_template('about.html',params=params)

@app.route("/dashboard", methods = ['GET','POST'])
def dashboard():
    if "user" in session and session['user'] == params['user_name']:
        post = blog.query.all()
        return render_template("dashboard.html", params=params, post=post)

    elif request.method=='POST':
        user_name = request.form.get('uname')
        user_pass = request.form.get('pass')

        if (user_name == params['user_name'] and user_pass == params['user_pass']):
            post = blog.query.all()
            return render_template('dashboard.html',params=params, post=post)
        else:
            return render_template('login.html',params=params)
    
    else:
        return render_template('login.html',params=params)
        
@app.route("/uploader" , methods=['GET', 'POST'])
def uploader():
    if "user" in session and session['user']==params['user_name']:
        if request.method=='POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully!"
    

@app.route("/contact", methods = ['GET','POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name, phone_num=phone, message=message, date_time=datetime.now(), email=email)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
                        sender = email,
                        recipients = [params['gmail-user']],
                        body = message + "\n" + phone
                        )
    return render_template('contact.html',params=params)

@app.route("/post/<string:blog_slug>", methods=['GET'])
def post(blog_slug):
    post = blog.query.filter_by(slug=blog_slug).first()
    return render_template('post.html',params=params, post=post)

@app.route("/add", methods = ['GET','POST'])
def add():
    if(request.method=='POST'):
        Title = request.form.get('title')
        Sub_heading = request.form.get('sub heading')
        Slug = request.form.get('slug')
        Content = request.form.get('content')
        Img_file = request.form.get('img_file')
        Name = request.form.get('name')
        Date = datetime.now()
        entry = blog(title=Title, sub_heading=Sub_heading, slug=Slug, content=Content, img_file=Img_file, name=Name, date=Date)
        db.session.add(entry)
        db.session.commit()
    
    return render_template('add.html',params=params)


@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    
        if(request.method=='POST'):
            title = request.form.get('title')
            sub_heading = request.form.get('sub heading')
            slug = request.form.get('slug')
            name = request.form.get('name')
            img_file = request.form.get('img_file')
            content = request.form.get('content')
            date = datetime.now()

            post = blog.query.filter_by(sno=sno).first()
            post.title = title
            post.sub_heading = sub_heading
            post.slug = slug
            post.name = name
            post.img_nfile = img_file
            post.content = content
            post.date = date
            db.session.commit()
            return redirect('/edit/'+sno)
        post = blog.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    
    post=blog.query.filter_by(sno=sno).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/dashboard")


@app.route("/logout")
def logout():
    if "user" in session and session['user'] == params['user_name']:
        session.pop('user')
    return redirect('/dashboard')
 
      
app.run(debug=True)