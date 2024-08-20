from flask import Flask, g
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import ui_client.routes.start as start
import ui_client.routes.messages as message
import ui_client.routes.assistant_page as assist
import ui_client.routes.stores_page as store
import ui_client.routes.threads_page as thread
from ui_control.command_processor import Commands
from ui_control.client_interface import ClientInterface


def create_app(secret_key, client_interface, assistant):
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = secret_key
    app.config['CLIENT_INTERFACE'] = client_interface    # SHOULD THIS USE THE app_context instead??
    app.config['RUN_SETUP'] = True                      # used in route '/' to see if this is the first time
    app.config['ASSISTANT'] = assistant                    # Current known assistant (should get from client)
    app.register_blueprint(start.bp)
    app.register_blueprint(message.msg)
    app.register_blueprint(assist.ap)
    app.register_blueprint(store.vect)
    app.register_blueprint(thread.thr)

    # Create a file handler
    file_handler = RotatingFileHandler('flask.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.INFO)  # This sets the minimum level for the file handler

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # This sets the minimum level for the console handler

    # Create a log formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add the handlers to the app's logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    with app.app_context():
        return app

