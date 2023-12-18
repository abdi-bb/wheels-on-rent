from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from .customer import login_required
from car_rental.db import db
from car_rental.models.booking import Booking
from car_rental.models.car import Car
from car_rental.models.customer import Customer
from car_rental.shared_variables import get_greeting
from datetime import date

from . import booking_bp


@booking_bp.route('/create/<int:car_id>', methods=('GET', 'POST'))
@login_required
def create(car_id):
    today_date = date.today()
    car = Car.query.get_or_404(car_id)
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        error = None

        if not start_date:
            error = 'Start date is required.'
        if not end_date:
            error = 'End date is required.'

        if error is not None:
            flash(error)
        else:
            customer_id = g.customer.id

            new_booking = Booking(
                car_id=car_id,
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date
            )
            db.session.add(new_booking)
            car.status = 0
            db.session.commit()
            flash('You have successfully booked your car!', 'success')
            return redirect(url_for('booking.my_bookings'))

    return render_template('booking/create.html', today_date=today_date, car=car)


@booking_bp.route('/my_bookings')
@login_required
def my_bookings():
    greeting = get_greeting()
    customer_id = g.customer.id

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

@booking_bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    booking = Booking.query.get_or_404(id)
    cars = Car.query.order_by(Car.name).all()

    if request.method == 'POST':
        if 'update' in request.form:
            car_id = request.form['car_id']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
        elif 'cancel' in request.form:
            return redirect(url_for('booking.my_bookings'))
        error = None

        if not start_date:
            error = 'Start date is required.'
        if not end_date:
            error = 'End date is required.'

        if error is not None:
            flash(error)
        else:
            db.session.query(Booking).filter_by(id=id).update({
                'car_id': car_id,
                'start_date': start_date,
                'end_date': end_date,
            })
            db.session.commit()
            return redirect(url_for('booking.my_bookings'))
        
    return render_template('booking/update.html', booking=booking, cars=cars)

@booking_bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    booking = Booking.query.get_or_404(id)
    car_id = booking.car_id
    db.session.delete(booking)
    
    Car.query.filter_by(id=car_id).update({'status': 1})
    db.session.commit()
    if g.customer.role == 1:
        return redirect(url_for('booking.index'))
    return redirect(url_for('booking.my_bookings'))



# Admin can see all bookings
@booking_bp.route('/')
@login_required
def index():
    bookings = Booking.query.join(Customer).join(Car).with_entities(
        Booking.id,
        Car.name.label('car_name'),
        Customer.name.label('customer_name'),
        Customer.last_name,
        Booking.start_date,
        Booking.end_date
    ).order_by(Booking.start_date.asc()).all()

    return render_template('admin/booking_list.html', bookings=bookings)



# # Getting booking with the same booking id
# def get_booking(id, check_author=True):
#      # Use SQLAlchemy queries to fetch the booking
#     booking = Booking.query.join(Customer).join(Car).filter(Booking.id == id).first()

#     if booking is None:
#         abort(404, f"Booking id {id} doesn't exist.")

#     # Check if the user is an admin (role == 1) or if the booking belongs to the user
#     if g.customer.role == 1 or (check_author and booking.customer_id == g.customer.id):
#         return booking
#     else:
#         abort(403)






@booking_bp.route('/check_and_update_car_status')
def check_and_update_car_status():
    today_date = date.today()
    expired_bookings = Booking.query.filter(Booking.end_date < today_date).all()

    for car_id in expired_bookings:
        car = Car.query.get(car_id)
        if car:
            car.status = 1

    Booking.query.filter(Booking.end_date < today_date).delete()
    db.session.commit()

    return 'Car statuses updated and expired bookings deleted.'
