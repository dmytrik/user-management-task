# User Management REST API

## Description
This project implements a **User Management REST API** built with **Flask** and **SQLAlchemy**. It provides CRUD operations to manage users in a relational database, with support for avatar image uploads stored in **Amazon S3**.

## Features
- Create a new user with optional avatar (`POST /users/`)
- Retrieve a list of all users (`GET /users/`)
- Get user details by ID (`GET /users/{id}/`)
- Update user details with required fields and optional avatar (`PUT /users/{id}/`)
- Delete a user (`DELETE /users/{id}/`)
- Database management using **SQLAlchemy**
- Avatar storage in **Amazon S3**
- API documentation with **Swagger (Flasgger)**
- Containerized using **Docker**
- Automated tests with **pytest** and **Poetry**

## Technologies Used
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database interaction
- **PostgreSQL / SQLite** - Database options (PostgreSQL for production, SQLite for testing)
- **Pydantic** - Data validation
- **boto3** - Amazon S3 integration
- **Docker & Docker Compose** - Containerization
- **Gunicorn** - Production WSGI server
- **Flasgger** - API documentation
- **pytest & Poetry** - Automated testing & dependency management

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL (for local or Docker deployment)
- Docker (for containerized deployment)
- Poetry for dependency management
- AWS account with S3 bucket and IAM credentials

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/dmytrik/user-management-task.git
   cd user-management-api
   ```

2. Configure environment variables in .env:
   ```
   ENVIRONMENT=local
   POSTGRES_NAME=
   POSTGRES_USER=
   POSTGRES_PASSWORD=
   POSTGRES_PORT=
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   AWS_S3_BUCKET=
   AWS_REGION=
   ```

3. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

4. Activate the virtual environment:
   ```sh
   poetry shell
   ```

5. Set up the database:
   ```sh
   alembic upgrade head
   ```

6. Run the application:
   ```sh
   gunicorn run:app -b 0.0.0.0:8000 --reload
   ```

## Running with Docker
1. Build and start the container:
   ```sh
   docker-compose up --build
   ```

2. The API will be available at: `http://localhost:8001/apidocs/`

## API Endpoints
| Method | Endpoint          | Description |
|--------|------------------|-------------|
| POST   | `/users/`        | Create a new user |
| GET    | `/users/`        | Retrieve all users |
| GET    | `/users/{id}/`   | Get a user by ID |
| PUT    | `/users/{id}/`   | Update a user by ID |
| DELETE | `/users/{id}/`   | Delete a user by ID |

## Running Tests
To execute the tests using Poetry, run:
```sh
poetry run pytest -v
```

## Author
Developed by **Samoylenko Dmytro**

