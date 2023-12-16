from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from .customer import login_required
from car_rental.db import db
from .car import get_car
from car_rental.models.booking import Booking
from car_rental.models.car import Car
from car_rental.models.customer import Customer
from car_rental.shared_variables import get_greeting, get_today_date

bp = Blueprint('booking', __name__, url_prefix='/wheels_on_rent/booking')


# Admin can see all bookings
@bp.route('/')
@login_required
def index():
    # Use SQLAlchemy to query bookings and related information
    bookings = Booking.query.join(Customer).join(Car).with_entities(
        Booking.id,
        Car.name.label('car_name'),
        Customer.name.label('customer_name'),
        Customer.last_name,
        Booking.start_date,
        Booking.end_date
    ).order_by(Booking.start_date.asc()).all()

    return render_template('admin/booking_index.html', bookings=bookings)


# Customer can see his own bookings
@bp.route('/my_bookings')
@login_required
def my_bookings():
    # Say Good Morning/Good Afternoon your customer
    greeting = get_greeting()

    # Get the customer_id of the logged-in user
    customer_id = g.customer.id

    # Use SQLAlchemy to query bookings for the logged-in customer
    bookings = Booking.query.join(Customer).join(Car).filter(
        Booking.customer_id == customer_id
    ).with_entities(
        Booking.id,
        Car.id.label('car_id'),
        Car.name.label('car_name'),
        Customer.id.label('customer_id'),
        Customer.name.label('customer_name'),
        Customer.last_name,
        Booking.start_date,
        Booking.end_date
    ).order_by(Booking.start_date.asc()).all()

    return render_template('booking/index.html', greeting=greeting, bookings=bookings)


@bp.route('/create/<int:car_id>', methods=('GET', 'POST'))
@login_required
def create(car_id):
    today_date = get_today_date()
    car = get_car(car_id)
    if request.method == 'POST':
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        error = None

        if not start_date_str:
            error = 'Start date is required.'
        if not end_date_str:
            error = 'End date is required.'

        if error is not None:
            flash(error)
        else:
            customer_id = g.customer.id

            new_booking = Booking(
                car_id=car_id,
                customer_id=customer_id,
                start_date=datetime.strptime(start_date_str, '%Y-%m-%d'),
                end_date=datetime.strptime(end_date_str, '%Y-%m-%d')
            )

            db.session.add(new_booking)
            
            # Update the car status to booked
            car.status = 0

            db.session.commit()
            flash('You have successfully booked your car!', 'success')
            return redirect(url_for('booking.my_bookings'))

    return render_template('booking/create.html', today_date=today_date, car=car)


# Getting booking with the same booking id
def get_booking(id, check_author=True):
     # Use SQLAlchemy queries to fetch the booking
    booking = Booking.query.join(Customer).join(Car).filter(Booking.id == id).first()

    if booking is None:
        abort(404, f"Booking id {id} doesn't exist.")

    # Check if the user is an admin (role == 1) or if the booking belongs to the user
    if g.customer.role == 1 or (check_author and booking.customer_id == g.customer.id):
        return booking
    else:
        abort(403)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    booking = get_booking(id)
    cars = Car.query.order_by(Car.name).all()

    if request.method == 'POST':
        if 'update' in request.form:
            car_id = request.form['car_id']
            start_date_str = request.form['start_date']
            end_date_str = request.form['end_date']
        elif 'cancel' in request.form:
            return redirect(url_for('booking.my_bookings'))
        error = None

        if not start_date_str:
            error = 'Start date is required.'
        if not end_date_str:
            error = 'End date is required.'

        if error is not None:
            flash(error)
        else:
            # Update the booking using SQLAlchemy
            db.session.query(Booking).filter_by(id=id).update({
                'car_id': car_id,
                'start_date': datetime.strptime(start_date_str, '%Y-%m-%d'),
                'end_date': datetime.strptime(end_date_str, '%Y-%m-%d'),
            })
            db.session.commit()
            return redirect(url_for('booking.my_bookings'))
        
    return render_template('booking/update.html', booking=booking, cars=cars)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    booking = Booking.query.get_or_404(id)
    car_id = booking.car_id  # Get the car_id associated with this booking
    
    # Delete the booking and update the car status using SQLAlchemy
    db.session.delete(booking)
    Car.query.filter_by(id=car_id).update({'status': 1})  # Update car status to 1 (available)
    
    db.session.commit()

    if g.customer.role == 1:
        return redirect(url_for('booking.index'))
    return redirect(url_for('booking.my_bookings'))


# This is a function to run periodicaly to check expired bookings
# To delete them
# This should be run at least once per a day
# This is an alternative automation if the customer or admin did not delete the expired booking
@bp.route('/check_and_update_car_status')
def check_and_update_car_status():
    # This route checks for cars with end dates that have passed
    # and updates their status to 1 (available for rent)

    today_date = get_today_date()

     # Step 1: Update car status
    expired_cars = Booking.query.filter(Booking.end_date < today_date).all()


    for car_id in expired_cars:
        car = Car.query.get(car_id)
        if car:
            car.status = 1

    # Step 2: Delete expired bookings
    Booking.query.filter(Booking.end_date < today_date).delete()
    db.session.commit()

    return 'Car statuses updated and expired bookings deleted.'
