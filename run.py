from flask import Flask
from flasgger import Swagger
from src.users.routes import router as users_router


def create_app():
    """Initialize and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(users_router)
    app.config["SWAGGER"] = {
        "title": "Users Management API",
    }
    Swagger(app)
    return app


app = create_app()

if __name__ == "__main__":
    """Run the Flask app locally if executed directly."""
    app.run(app, host="0.0.0.0", port=8000)
