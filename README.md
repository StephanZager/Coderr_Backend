# Coderr Backend

This is the backend for the Coderr application, a platform designed to connect customers and businesses. It is built with Django and Django REST Framework.

## Getting Started

You can run this project in two ways: using Docker (recommended for a consistent environment that mirrors production) or locally with a Python virtual environment.

### Option 1: Running with Docker (Recommended)

This method uses Docker and Docker Compose to set up the entire environment, including the Django application and a PostgreSQL database.

#### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)

#### 1. Clone the Repository

```bash
git clone https://github.com/StephanZager/Coderr_Backend
cd Coderr_Backend
```

#### 2. Create Environment File

Create a `.env` file in the root directory of the backend. This file will hold your environment variables. For a local development setup, you can use the following content:

```
# Django Settings
DJANGO_SECRET_KEY=django-insecure-dev-key-for-local-docker-setup
DEBUG=1

# Postgres Settings
POSTGRES_DB=coderr_db
POSTGRES_USER=coderr_user
POSTGRES_PASSWORD=coderr_password
```

#### 3. Build and Run the Containers

Use Docker Compose to build the images and start the containers in the background.

```bash
docker-compose up --build -d
```

The `web` (Django) and `db` (PostgreSQL) services will now be running.

#### 4. Apply Database Migrations

Run the database migrations inside the `web` container to set up the database schema.

```bash
docker-compose exec web python manage.py migrate
```

The backend will now be accessible at `http://127.0.0.1:8000/`.

#### 5. (Optional) Create a Superuser

To access the Django admin panel, you can create a superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

---

### Option 2: Running Locally with a Virtual Environment

This method is for running the project directly on your machine without Docker.

#### Prerequisites

- Python 3.x

#### 1. Clone the Repository

```bash
git clone https://github.com/StephanZager/Coderr_Backend
cd Coderr_Backend
```

#### 2. Create and Activate a Virtual Environment

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

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Apply Database Migrations

This setup uses a simple `db.sqlite3` file for the database.
```bash
python manage.py migrate
```

#### 5. Start the Development Server

```bash
python manage.py runserver
```

The backend will now be accessible at `http://127.0.0.1:8000/`.

## Running Tests

To run the test suite, use the command corresponding to your setup method.

**With Docker:**
```bash
docker-compose exec web python manage.py test
```

**Locally:**
```bash
python manage.py test
```

To run tests for a specific app (e.g., `orders_app`):

**With Docker:**
```bash
docker-compose exec web python manage.py test orders_app
```

**Locally:**
```bash
python manage.py test orders_app
```