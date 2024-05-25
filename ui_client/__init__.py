from flask import Flask
from config import Config
import ui_client.start as start


def create_app(secret_key):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = secret_key
    app.register_blueprint(start.bp)

    with app.app_context():
        return app

