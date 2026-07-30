from asyncio import events

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import date, datetime
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pro_secret_key_99'

raw_db_url = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = raw_db_url.replace("postgres://", "postgresql://", 1) if raw_db_url else 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.String(50))
    description = db.Column(db.Text)
    trainee_name = db.Column(db.String(40))
    members = db.Column(db.Integer)
    feeback = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    content = db.Column(db.Text)
    
class Student(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    register = db.Column(db.String(15))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    number = db.Column(db.Integer)
    collage = db.Column(db.String(100))
    academic_year = db.Column(db.String(30))
    intern_start_date = db.Column(db.String(30))
    degree = db.Column(db.String(100))
    department = db.Column(db.String(100))
    payment = db.Column(db.String(10))
    status = db.Column(db.String(20))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='alpha').first():
        db.session.add(User(username='alpha', password='alpha2026'))
        db.session.commit()

@app.route('/')
def home():
    classes = Class.query.all()
    return render_template('index.html', classes=classes)

@app.route('/contact', methods=['POST'])
def send_message():
    new_msg = Message(
        name=request.form.get('name'),
        email=request.form.get('email'),
        content=request.form.get('content')
    )
    db.session.add(new_msg)
    db.session.commit()
    flash('Message sent successfully!')
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            login_user(user)
            return redirect(url_for('admin_panel'))
        flash('Invalid Credentials')
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin_panel():
    classes = Class.query.all()
    messages = Message.query.all()
    return render_template('admin.html', classes=classes, messages=messages)

@app.route('/admin/add_class', methods=['POST'])
@login_required
def add_class():
    db.session.add(Class(
        title=request.form.get('title'),
        date=request.form.get('date'),
        description=request.form.get('description'),
        trainee_name=request.form.get('trainee_name'),
        members=request.form.get('members'),
        feeback=request.form.get('feeback'),
        created_at=datetime.utcnow()
    ))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_class(id):
    classes = Class.query.get_or_404(id)
    if request.method == 'POST':
        classes.title = request.form.get('title')
        classes.date = request.form.get('date')
        classes.description = request.form.get('description')
        classes.trainee_name = request.form.get('trainee_name')
        classes.members = request.form.get('members')
        classes.feeback = request.form.get('feeback')
        classes.created_at = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('updated.html', classes=classes)

@app.route('/admin/add_student',methods=['GET','POST'])
def add_student():
    if request.method == 'POST':
        new_student = Student(
            register=request.form.get('register'),
            name=request.form.get('name'),
            email=request.form.get('email'),
            number=request.form.get('number'),
            collage=request.form.get('collage'),
            academic_year=request.form.get('academic_year'),
            intern_start_date=request.form.get('intern_start_date'),
            degree=request.form.get('degree'),
            department=request.form.get('department'),
            payment=request.form.get('payment'),
            status=request.form.get('status')
        )
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('admin_panel'))
    return render_template('add_student.html')

@app.route('/student_details',methods=['GET','POST'])
def student_details() :
    students = Student.query.all()
    return render_template('student_details.html',  students=students)


@app.route('/admin/delete_class/<int:id>')
@login_required
def delete_class(id):
    db.session.delete(Class.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_msg/<int:id>')
@login_required
def delete_msg(id):
    db.session.delete(Message.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)