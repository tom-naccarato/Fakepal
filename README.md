
# FakePal: An Online Payment Service

**Version**: 1.0.0  
**Django Version**: 5.0.2  
**Python Version**: 3.10  
**Deployment**: AWS EC2  
**Database**: SQLite

## Project Overview

FakePal is a secure online payment service built using the Django framework. The application supports essential functionalities such as user registration, direct money transfers, payment requests, and transaction tracking. While FakePal simulates a real online payment system, it does not connect to actual bank accounts. Instead, each user is provided with a simulated account balance upon registration.

The project is fully implemented and hosted on AWS, and it includes a responsive front-end designed with Bootstrap 5 and Crispy Forms, ensuring compatibility across desktop and mobile devices.

## Key Features

1. **User Registration and Login**:
   - Users can register an account and are automatically provided with a starting balance of £1000.
   - After registration, users can log in to access the platform's features.

2. **Direct Money Transfers**:
   - Users can transfer funds to other users within the system.
   - Each transaction is handled securely using Django's `@transaction.atomic` decorator to ensure ACID properties.

3. **Payment Requests**:
   - Users can request payments from others, which can be accepted, declined, or canceled.
   - Notifications are provided for all actions related to requests.

4. **Transaction and Request Tracking**:
   - Users can view all their transactions and requests at any time, with each entry timestamped using an Apache Thrift service.

5. **Administrative Functions**:
   - Admins can manage all users, view all transactions, and register new administrators.

6. **Currency Conversion**:
   - A RESTful web service handles currency conversion, although the rates are hard-coded for simplicity.

7. **Security**:
   - Full HTTPS communication for all interactions.
   - Protection against XSS, CSRF, and SQL injection through Django’s middleware and ORM.

8. **Cloud Deployment**:
   - The application is deployed using Nginx and Gunicorn on AWS, with automated service management to ensure continuous availability.

## Installation and Setup

### Local Development

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/fakepal.git
   cd fakepal
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the Application**:

You can access the application from [here](https://ec2-52-203-137-55.compute-1.amazonaws.com/webapps2024/).

## Usage

### User Actions

- **Register/Login**: Create an account or log in to an existing one.
- **Transfers**: Send money to other users within the platform.
- **Requests**: Request payments from other users and manage received requests.
- **Notifications**: Keep track of transaction statuses through the notification system.

### Admin Actions

- **Manage Users**: View and manage all registered users.
- **View Transactions**: Monitor all transactions and requests across the platform.
- **Register Admins**: Add new administrators to the system.

## Testing

Unit tests have been provided to ensure the functionality of the application. To run the tests:

```bash
python manage.py test
```

## Documentation

Detailed documentation is provided and generated using Sphinx. For a complete guide to the project, refer to the documentation included in the project files.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
