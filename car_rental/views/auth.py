# Getting customer id that was previously stored during login
import functools
from flask import g, redirect, session, url_for

from car_rental.models.customer import Customer
from . import customer_bp


@customer_bp.before_app_request
def load_logged_in_customer():
    customer_id = session.get('customer_id')

    if customer_id is None:
        g.customer = None
    else:
        g.customer = Customer.query.get(customer_id)


# logging out a customer by clearing customer id from the session
@customer_bp.route('/logout')
def logout():
    # Clear the user's session data
    session.pop('customer_id', None)
    return redirect(url_for('home'))


# Use the after_request decorator to add a response header
@customer_bp.after_request
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
            return redirect(url_for('customer.login'))

        return view(**kwargs)

    return wrapped_view