import functools
from flask import flash, g, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from car_rental.db import db

from car_rental.models.user import User
from . import auth_bp


# User login control
@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        error = None
        
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            error = 'Incorrect email or password, please try again!'
            
        if error is None:
            login_user(user, remember=remember)
            if user.role == 1:
                return redirect(url_for('user.admin_dashboard'))
            return redirect(url_for('car.available'))

        flash(error, 'error')

    return render_template('auth/login.html')



@auth_bp.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        password = request.form.get('password')
        error = None

        error = (
                'All fields are required.'
                if not (name or last_name or phone_number or email or password)
                else None
            )

        if error is None:
            try:
                user_count = User.query.count()
                
                new_user = User(
                    name=name,
                    last_name=last_name,
                    phone_number=phone_number,
                    email=email,
                    role=1 if user_count < 1 else 0,
                    password=generate_password_hash(password)
                    
                )
                db.session.add(new_user)
                db.session.commit()
                flash('You have registered successfully.', 'success')
            except db.exc.IntegrityError:
                error = f"Email {email} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error, 'error')

    return render_template('auth/login.html')



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))