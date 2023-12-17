from car_rental.config import create_app
from car_rental.db import db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
