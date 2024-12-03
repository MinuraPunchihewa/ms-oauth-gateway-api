import os

from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')

    from routes import register_routes

    register_routes(app)

    return app