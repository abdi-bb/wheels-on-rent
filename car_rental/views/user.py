from flask import (
    flash, g, redirect, render_template, request, session, url_for
)
from flask_login import login_required
from werkzeug.security import  generate_password_hash, check_password_hash

from car_rental.db import db
from car_rental.models.booking import Booking
from car_rental.models.car import Car
from car_rental.models.user import User

from . import user_bp


@user_bp.route('/')
@login_required
def index():
    users = User.query.filter_by(role=0).order_by(User.name.asc()).all()

    return render_template('admin/user_list.html', users=users)


@user_bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    user = User.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name')
        last_name = request.form.get('last_name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        new_password = request.form.get('password')
        confirm_new_password = request.form.get('confirm_password')
        error = None

        if not name or not last_name or not phone_number or not email:
            error = 'All fields are required.'
        elif new_password != confirm_new_password:
            error = 'Passwords do not match.'
        else:
            user.name = name
            user.last_name = last_name
            user.phone_number = phone_number
            user.email = email
            if new_password:
                user.password = generate_password_hash(new_password)

            db.session.commit()
            flash('Profile updated successfully.', 'success')

            if user.role == 0:
                return redirect(url_for('car.available'))
            elif user.role == 1:
                return redirect(url_for('user.admin_dashboard'))

        flash(error, 'error')
        
    template = 'admin/update.html' if user.role == 1 else 'user/update.html'

    return render_template(template)


@user_bp.route('/<int:id>/delete', methods=('POST', 'DELETE',))
@login_required
def delete(id):
    user = User.query.get_or_404(id)

    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            flash('User deleted successfully.', 'success')
        except Exception:
            flash('You can not delete this user, as it has a booking tied to it!', 'error')
    else:
        flash('User not found.', 'error')

    return redirect(url_for('user.index'))


@user_bp.route('/<int:id>/staff', methods=('POST',))
@login_required
def upgrade_user(id):
    user = User.query.get_or_404(id)
    staff = False
    
    if user:
        if user.id == g.user.id:
            staff = True
            flash("Suicide is illegal! Let another admin handle it.", 'error')
        else:
            if user.role == 0:
                user.role = 1
                staff = True
            elif user.role == 1:
                user.role = 0
                staff = False
            db.session.commit()
            flash('User level updated successfully.', 'success')
    else:
        flash('User not found.', 'error')

    if staff:
        return redirect(url_for('user.staff_members'))
    else:
        return redirect(url_for('user.index'))
    

@user_bp.route('/staff_members')
@login_required
def staff_members():
    staff_list = User.query.filter_by(role=1).order_by(User.name.asc()).all()
    return render_template('admin/staff_list.html', staff_list=staff_list)



@user_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    staff_count = User.query.filter_by(role=1).count()
    car_count = Car.query.count()
    user_count = User.query.filter(User.role != 1).count()
    booking_count = Booking.query.count()

    return render_template('admin/dashboard.html',
                           staff_count=staff_count,
                           car_count=car_count,
                           user_count=user_count,
                           booking_count=booking_count)