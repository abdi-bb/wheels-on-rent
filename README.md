# WheelsOnRent Car Rental System

Welcome to WheelsOnRent, a car rental system that allows you to rent cars and manage your car rental business seamlessly. This README will guide you through setting up and running the application locally.

## Getting Started

To get started with WheelsOnRent, follow these steps after cloning the repository:

1. Clone to the public repository
   
   ```bash
   https://github.com/abdi-bb/wheels-on-rent.git
   ```

2. Change your current directory to the project folder:

   ```bash
   cd wheels-on-rent
   ```

3. Create python venv
   
   ```bash
   python3 -m venv carvenv
   ```

4. Activate virtual environment
   
   ```bash
   source carvenv/bin/activate
   ```

5. Install project requirements inside venv
   
   ```bash
   pip install -r requirements.txt
   ```

6. Initialize the database by running the following command:

   ```bash
   flask init-db
   ```

   This command will create the necessary database tables.

7. Run the application:

   ```bash
   python wsgi.py
   ```

   The application will start, and you can access it by opening your favorite web browser and navigating to [http://127.0.0.1:5000](http://127.0.0.1:5000).


## Authors

- Abdi Berhe
  - GitHub: [abdi8-GitHub](https://github.com/abdi8-GitHub/)
  - LinkedIn: [Abdi Berhe on LinkedIn](https://www.linkedin.com/in/abdi-berhe)

- Addis Simegn
  - GitHub: [Addika1630](https://github.com/Addika1630/)
  - LinkedIn: [Addis Simegn on LinkedIn](https://www.linkedin.com/in/your-linkedin-profile/)

- Daniel Tsega
  - GitHub: [DannySanchez6658](https://github.com/DannySanchez6658/)
  - LinkedIn: [Daniel Tsega on LinkedIn](https://www.linkedin.com/in/your-linkedin-profile/)

Feel free to reach out to the authors for any questions or contributions related to the project.

Happy renting! 🚗
