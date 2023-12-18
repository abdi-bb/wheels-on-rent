from flask import Blueprint


booking_bp = Blueprint('booking', __name__, url_prefix='/wheels_on_rent/booking')
car_bp = Blueprint('car', __name__, url_prefix='/wheels_on_rent/car')
user_bp = Blueprint('user', __name__, url_prefix='/wheels_on_rent/user')
auth_bp = Blueprint('auth', __name__, url_prefix='/wheels_on_rent/auth')
