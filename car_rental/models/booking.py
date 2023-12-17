from car_rental.db import db

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    end_date = db.Column(db.Date, nullable=False, default=db.func.current_date())
    customer = db.relationship('Customer', backref='bookings')
    car = db.relationship('Car', backref='bookings')
