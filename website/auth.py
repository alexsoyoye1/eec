from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from website.models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first() 
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password', category='error')
        else:
            flash('Username does not exist', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if current_user.department=="IT" and current_user.head_status=="Yes":

        if request.method == 'POST':
            email = request.form.get('email')
            username = request.form.get('username')
            staff_name = request.form.get('staffName')
            password1 = request.form.get('password1')
            password2 = request.form.get('password2')
            location = request.form.get('location')
            department = request.form.get('department')
            linemanager_status=request.form.get('linemanager_status')
            head_status=request.form.get('head_status')
            
            user = User.query.filter_by(username=username).first()
            if user:
                flash('Username already exists', category='error')
            elif len(email) < 4:
                flash('Email Must be greater than 3 characters.', category='error')
            elif len(staff_name) < 2:
                flash('First Name Must be greater than 1 characters.', category='error')
            elif password1 != password2:
                flash('Passwords don\'t match.', category='error')
            elif len(password1) < 3:
                flash('Password Must be greater than 2 characters.', category='error')
            else:
                new_user= User(email=email, username=username, staff_name=staff_name, password=generate_password_hash(password1,method='sha256'),
                department=department, location=location, linemanager_status=linemanager_status,head_status=head_status)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account Created!', category='success')
                
                return redirect(url_for('views.home'))

        return render_template("sign_up.html", user=current_user)

    else:
        flash('You do not have access to this page', category='error')
        return redirect(url_for('views.home'))