from car_rental.db import db

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    seat = db.Column(db.Integer, nullable=False)
    door = db.Column(db.Integer, nullable=False)
    gearbox = db.Column(db.String(255), nullable=False)
    image = db.Column(db.LargeBinary, nullable=False)
    price = db.Column(db.String(255), nullable=False)
