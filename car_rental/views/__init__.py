from flask import Blueprint


booking_bp = Blueprint('booking', __name__, url_prefix='/wheels_on_rent/booking')
car_bp = Blueprint('car', __name__, url_prefix='/wheels_on_rent/car')
customer_bp = Blueprint('customer', __name__, url_prefix='/wheels_on_rent/customer')
