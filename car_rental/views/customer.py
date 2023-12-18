import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from car_rental.db import db
from car_rental.models.booking import Booking
from car_rental.models.car import Car
from car_rental.models.customer import Customer
from car_rental.views.auth import login_required

from . import customer_bp


@customer_bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        error = None

        if not name:
            error = 'Name is required.'
        elif not last_name:
            error = 'Last Name is required.'
        elif not phone_number:
            error = 'Phone Number is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                new_customer = Customer(
                    name=name,
                    last_name=last_name,
                    phone_number=phone_number,
                    email=email,
                    password=generate_password_hash(password)
                )
                db.session.add(new_customer)
                db.session.commit()
                flash('You have registered successfully.', 'success')
            except db.exc.IntegrityError:
                error = f"Email {email} is already registered."
            else:
                return redirect(url_for("customer.login"))

        flash(error, 'error')

    return render_template('customer/login.html')

@customer_bp.route('/')
@login_required
def index():
    customers = Customer.query.filter_by(role=0).order_by(Customer.name.asc()).all()

    return render_template('admin/customer_index.html', customers=customers)



# Customer login control
@customer_bp.route('/login', methods=('GET', 'POST'))
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

    return render_template('customer/login.html')




# customer can be created by the logged in addmin
@customer_bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        error = None

        if not name:
            error = 'Name is required.'
        elif not last_name:
            error = 'Last Name is required.'
        elif not phone_number:
            error = 'Phone Number is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            # Create a new Customer using SQLAlchemy
            new_customer = Customer(
                name=name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                password=generate_password_hash(password)
            )

            # Add the new customer to the session and commit to the database
            db.session.add(new_customer)
            db.session.commit()

            flash('You have registered successfully.')
            return redirect(url_for("customer.index"))

        flash(error)

    return render_template('admin/customer_create.html')


## Admin can update customer table ##
# Get the customer to be updated
def get_customer(id, check_author=True):
    customer = Customer.query.get(id)

    if customer is None:
            abort(404, f"Customer id {id} doesn't exist.")

    return customer

# Update the customer
@customer_bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        error = None

        if not name:
            error = 'Name is required.'
        elif not last_name:
            error = 'Last Name is required.'
        elif not phone_number:
            error = 'Phone Number is required.'
        elif not email:
            error = 'Email is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'

        if error is not None:
            flash(error)
        else:
            customer = Customer.query.get(g.customer.id)

            if customer is not None:
                # Update customer fields
                db.session.query(Customer).filter_by(id=id).update({
                    'name': name,
                    'last_name': last_name,
                    'phone_number': phone_number,
                    'email': email,
                    'password': generate_password_hash(password),
                })
                db.session.commit()
                flash('Profile updated successfully.')
                return redirect(url_for('car.available'))
            else:
                flash('Customer not found.', 'error')

    return render_template('customer/update.html')


@customer_bp.route('/edit_profile', methods=('GET', 'POST'))
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        error = None

        if not name:
            error = 'Name is required.'
        elif not last_name:
            error = 'Last Name is required.'
        elif not email:
            error = 'Email is required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'

        if error is None:
            # Fetch the customer from the database
            customer = Customer.query.get(g.customer.id)

            if customer is not None:
                db.session.query(Customer).filter_by(id=id).update({
                    'name': name,
                    'last_name': last_name,
                    'email': email,
                    'password': generate_password_hash(password),
                })
                db.session.commit()
                flash('Profile updated successfully.')
                return redirect(url_for('customer.admin_dashboard'))
            else:
                flash('Customer not found.', 'error')

        flash(error)

    return render_template('admin/admin_update.html')



@customer_bp.route('/<int:id>/delete', methods=('POST', 'DELETE',))
@login_required
def delete(id):
    get_customer(id)
    customer = Customer.query.get(id)

    if customer:
        # Delete the customer from the database
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully.', 'success')
    else:
        flash('Customer not found.', 'error')

    return redirect(url_for('customer.index'))


# Admin Home(Dashboard)
@customer_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    # Count records in each table using SQLAlchemy
    car_count = Car.query.count()
    customer_count = Customer.query.count()
    booking_count = Booking.query.count()

    # Render the dashboard template and pass counts as context
    return render_template('admin/admin_dashboard.html',
                           car_count=car_count,
                           customer_count=customer_count,
                           booking_count=booking_count)