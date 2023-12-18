import os
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for,current_app
)
from werkzeug.exceptions import abort

from .customer import login_required
from car_rental.db import db
from car_rental.models.car import Car
from car_rental.shared_variables import get_greeting

from . import car_bp

@car_bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        model = request.form['model']
        status = request.form['status']
        seat = request.form['seat']
        door = request.form['door']
        gearbox = request.form['gearbox']
        image = request.files['image']
        price = request.form['price']
        error = None

        if not name:
            error = 'Name is required.'
        if not model:
            error = 'Model is required.'
        if not status:
            error = 'Status is required.'
        if not seat:
            error = 'Seat is required.'
        if not door:
            error = 'Door is required.'
        if not gearbox:
            error = 'Gearbox is required.'
        if not price:
            error = 'Price is required.'

        if error is not None:
            flash(error)
        else:
            if image and allowed_file(image.filename):
                image_data = image.read()

                new_car = Car(
                    name=name,
                    model=model,
                    status=status,
                    seat=seat,
                    door=door,
                    gearbox=gearbox,
                    image=image_data,
                    price=price
                )
                db.session.add(new_car)
                db.session.commit()
                
                flash('Car entry created successfully.', 'success')
                return redirect(url_for('car.index'))
            else:
                flash('Invalid or missing image.')

    return render_template('admin/car_create.html')


@car_bp.route('/')
@login_required
def index():
    cars = Car.query.order_by(Car.name.asc()).all()
    return render_template('admin/car_index.html', cars=cars)


@car_bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    car = Car.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form['name']
        model = request.form['model']
        status = request.form['status']
        seat = request.form['seat']
        door = request.form['door']
        gearbox = request.form['gearbox']
        image = request.files['image']
        price = request.form['price']
        error = None

        if not name:
            error = 'Name is required.'
        if not model:
            error = 'Model is required.'
        if not status:
            error = 'Status is required.'
        if not seat:
            error = 'Seat is required.'
        if not door:
            error = 'Door is required.'
        if not gearbox:
            error = 'Gearbox is required.'
        if not price:
            error = 'Price is required.'

        if error is not None:
            flash(error)
        else:
            db.session.query(Car).filter_by(id=id).update({
                'name': name,
                'model': model,
                'status': status,
                'seat': seat,
                'door': door,
                'gearbox': gearbox,
                'price': price
            })

            if image and allowed_file(image.filename):
                image_data = image.read()
                db.session.query(Car).filter_by(id=id).update({'image': image_data})

            db.session.commit()
            return redirect(url_for('car.index'))

    return render_template('admin/car_update.html', car=car)


@car_bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    car = Car.query.get_or_404(id)
    db.session.delete(car)
    db.session.commit()
    
    return redirect(url_for('car.index'))




# Function to check if a file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Function to get the path for uploaded files
def get_upload_path(filename):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)



# Car list for customer
@car_bp.route('/available')
@login_required
def available():
    greeting = get_greeting()
    cars = Car.query.filter_by(status=1).order_by(Car.name.asc()).all()

    return render_template('car/index.html', greeting=greeting, cars=cars)


@car_bp.route('/guest_mode')
def guest_mode():
    guest = 1
    cars = Car.query.filter_by(status=1).order_by(Car.name.asc()).all()

    return render_template('car/index.html', guest=guest, cars=cars)




# # Getting a car associated with a given id to update it
# def get_car(id, check_author=True):
#     car = db.session.query(Car).filter_by(id=id).first()

#     if car is None:
#         abort(404, f"Car id {id} doesn't exist.")

#     return car
