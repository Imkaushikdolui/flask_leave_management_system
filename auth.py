from flask import Blueprint, render_template, url_for, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, logout_user, login_required, current_user

auth = Blueprint('auth',__name__)


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup',methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    role = request.form.get('role')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user:
        return("user already exists")
        
    new_user = User(email=email, name=name, role=role, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    flash('Successfully signed up')
    return redirect(url_for('auth.login'))
    

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login',methods=['POST'])
def login_post():
    
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password, password):
        return redirect(url_for('auth.login'))
    
    login_user(user)
    
    return redirect(url_for('auth.employee_dashboard'))

@auth.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.is_admin():
        # Only admins can access this view
        return render_template('admin_dashboard.html')
    else:
        # Redirect to a different page or show an error message
        return redirect(url_for('auth.employee_dashboard'))

@auth.route('/employee_dashboard')
@login_required
def employee_dashboard():
    if current_user.is_employee():
        # Only employees can access this view
        return render_template('employee_dashboard.html')
    else:
        # Redirect to a different page or show an error message
        return redirect(url_for('auth.admin_dashboard'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.home"))
