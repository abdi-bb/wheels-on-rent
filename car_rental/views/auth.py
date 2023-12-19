import functools
from flask import flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from car_rental.models.user import User
from . import auth_bp


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)



# Use the after_request decorator to add a response header
@auth_bp.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



# login_required decorator for login requiring views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# User login control
@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        
        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(user.password, password):
            error = 'Incorrect email or password, please try again!'
            
        if error is None:
            session.clear()
            session['user_id'] = user.id
            if user.role == 1:
                return redirect(url_for('user.admin_dashboard'))
            return redirect(url_for('car.available'))

        flash(error, 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))