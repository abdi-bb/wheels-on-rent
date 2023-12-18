import functools
from flask import flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from car_rental.models.customer import Customer
from . import auth_bp


@auth_bp.before_app_request
def load_logged_in_customer():
    customer_id = session.get('customer_id')

    if customer_id is None:
        g.customer = None
    else:
        g.customer = Customer.query.get(customer_id)



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
        if g.customer is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

# Customer login control
@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None
        
        customer = Customer.query.filter_by(email=email).first()

        if customer is None or not check_password_hash(customer.password, password):
            error = 'Incorrect email or password, please try again!'
            
        if error is None:
            session.clear()
            session['customer_id'] = customer.id
            if customer.role == 1:
                return redirect(url_for('customer.admin_dashboard'))
            return redirect(url_for('car.available'))

        flash(error, 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.pop('customer_id', None)
    return redirect(url_for('home'))