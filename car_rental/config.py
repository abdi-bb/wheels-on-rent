import os
from flask import Flask, send_from_directory, url_for, send_file, Response, render_template, redirect


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    # Set strict_slashes=False to allow flexibility with trailing slashes
    app.url_map.strict_slashes = False

    @app.route('/uploads/<int:car_id>')
    def uploaded_image(car_id):
        # Fetch the image data from the database
        car = Car.query.filter_by(id=car_id).first()

        if car is not None:
            image_data = car.image
            # Return the image data as a response
            return Response(image_data, content_type='image/jpeg')

    # Update the SQLALCHEMY_DATABASE_URI to use MySQL
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     SQLALCHEMY_DATABASE_URI='sqlite:///car_app.sqlite',
    #     SQLALCHEMY_TRACK_MODIFICATIONS=False,
    # )
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://car_rental_usr:car_rental_pwd@localhost/car_rental_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev'  # Add your own secret key here

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

     # Welcome page
    @app.route('/')
    def welcome():
        return render_template('welcome.html')

    # a simple page that says hello
    @app.route('/wheels_on_rent/')
    def home():
        return render_template('home.html')

    from .models.car import Car  # Import the Car model
    from . import db
    db.init_app(app)

    from .views import customer
    app.register_blueprint(customer.bp)

    from .views import booking
    app.register_blueprint(booking.bp)

    from .views import car
    app.register_blueprint(car.bp)

    return app
