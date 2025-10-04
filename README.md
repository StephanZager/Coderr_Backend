# Coderr Backend

This is the backend for the Coderr application, a platform designed to connect customers and businesses. It is built with Django and Django REST Framework.

## Setup

Follow the steps below to set up and run the project locally.

### Prerequisites

Ensure that you have Python 3 installed on your system. You can check this by running the following in your terminal:

```bash
python --version
```

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/StephanZager/Coderr_Backend
cd coderr_backend
```

### 2. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to keep the project's dependencies isolated.

**On macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

Once activated, your terminal prompt will be prefixed with the name of the virtual environment (e.g., `(venv)`).

### 3. Install Dependencies

Install all the required packages using pip and the requirements.txt file:

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

Apply the database migrations to set up your database schema:

```bash
python manage.py migrate
```

### 5. Start the Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The backend will now be accessible at `http://127.0.0.1:8000/`.

## Running Tests

The project includes a suite of tests to ensure the functionality of the API endpoints.

To run all the tests, use the following command:

```bash
python manage.py test
```

If you want to run tests for a specific app, you can specify the app's name. For example, to run the tests for the orders_app:

```bash
python manage.py test orders_app
```