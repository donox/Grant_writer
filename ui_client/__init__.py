from flask import Flask, g
from db_management.db_utils import close_db_manager
import sqlite3
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import ui_client.routes.start as start
import ui_client.routes.messages as message
import ui_client.routes.assistant_page as assist
import ui_client.routes.stores_page as store
import ui_client.routes.threads_page as thread
import ui_client.routes.generics as generics
import ui_client.routes.conversations as conversation


# THIS NEEDS path_to_db parameter if running configuratin pytest_grant_assistant
def create_app(secret_key, client_interface, assistant):
    app = Flask(__name__)
    app.logger.setLevel(logging.DEBUG)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = secret_key
    app.config['CLIENT_INTERFACE'] = client_interface    # SHOULD THIS USE THE app_context instead??
    app.config['RUN_SETUP'] = True                      # used in route '/' to see if this is the first time
    app.config['ASSISTANT'] = assistant                    # Current known assistant (should get from client)
    app.config['ENV'] = 'development'
    app.register_blueprint(start.bp)
    app.register_blueprint(message.msg)
    app.register_blueprint(assist.ap)
    app.register_blueprint(store.vect)
    app.register_blueprint(thread.thr)
    app.register_blueprint(generics.gen)
    app.register_blueprint(conversation.conv)

    # Create a file handler
    file_handler = RotatingFileHandler('flask.log', maxBytes=10240, backupCount=10)
    file_handler.setLevel(logging.DEBUG)  # This sets the minimum level for the file handler

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

    # Register the `close_db` function to be called after every request
    app.teardown_appcontext(close_db_manager)

    with app.app_context():
        return app

