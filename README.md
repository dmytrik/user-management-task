# User Management REST API

## Description
This project implements a simple **User Management REST API** using **Flask** and **SQLAlchemy**. It provides CRUD operations to manage users in a relational database.

## Features
- Create a new user (`POST /users`)
- Retrieve a list of all users (`GET /users`)
- Get user details by ID (`GET /users/{id}`)
- Update user details (`PUT /users/{id}`)
- Delete a user (`DELETE /users/{id}`)
- Database management using **SQLAlchemy**
- API documentation with **Swagger (Flasgger)**
- Containerized using **Docker**
- Automated tests with **pytest** and **Poetry**

## Technologies Used
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database interaction
- **PostgreSQL / SQLite** - Database options
- **Pydantic** - Data validation
- **Docker & Docker Compose** - Containerization
- **Gunicorn** - Production WSGI server
- **Flasgger** - API documentation
- **pytest & Poetry** - Automated testing & dependency management

## Installation

### Prerequisites
- Python 3.10+
- PostgreSQL or SQLite
- Docker (if using containerized deployment)
- Poetry for dependency management

### Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/user-management-api.git
   cd user-management-api
   ```

2. Install dependencies using Poetry:
   ```sh
   poetry install
   ```

3. Activate the virtual environment:
   ```sh
   poetry shell
   ```

4. Set up the database:
   ```sh
   alembic upgrade head
   ```

5. Run the application:
   ```sh
   gunicorn run:app -b 0.0.0.0:8000 --reload
   ```

## Running with Docker
1. Build and start the container:
   ```sh
   docker-compose up --build
   ```

2. The API will be available at: `http://localhost:8000`

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

