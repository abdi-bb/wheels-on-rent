import functools

from flask import (
    flash, g, redirect, render_template, request, session, url_for
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
                return redirect(url_for("auth.login"))

        flash(error, 'error')

    return render_template('auth/login.html')

@customer_bp.route('/')
@login_required
def index():
    customers = Customer.query.filter_by(role=0).order_by(Customer.name.asc()).all()

    return render_template('admin/customer_list.html', customers=customers)


@customer_bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    customer = Customer.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form['name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        error = None

        if not name or not last_name or not phone_number or not email:
            error = 'All fields are required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        else:
            customer.name = name
            customer.last_name = last_name
            customer.phone_number = phone_number
            customer.email = email
            customer.password = generate_password_hash(password)

            db.session.commit()
            flash('Profile updated successfully.', 'success')

            if customer.role == 0:
                return redirect(url_for('car.available'))
            elif customer.role == 1:
                return redirect(url_for('customer.admin_dashboard'))

        flash(error, 'error')
        
    template = 'admin/update.html' if customer.role == 1 else 'customer/update.html'

    return render_template(template)


@customer_bp.route('/<int:id>/delete', methods=('POST', 'DELETE',))
@login_required
def delete(id):
    customer = Customer.query.get_or_404(id)

    if customer:
        db.session.delete(customer)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('customer.index'))


@customer_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    car_count = Car.query.count()
    customer_count = Customer.query.count()
    booking_count = Booking.query.count()

    return render_template('admin/dashboard.html',
                           car_count=car_count,
                           customer_count=customer_count,
                           booking_count=booking_count)