from flask import Flask, g
from config import Config
import ui_client.routes.start as start
import ui_client.routes.messages as message
import ui_client.routes.assistant_page as assist
from ui_control.command_processor import Commands
from ui_control.client_interface import ClientInterface


def create_app(secret_key, client_interface, assistant):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = secret_key
    app.config['CLIENT_INTERFACE'] = client_interface    # SHOULD THIS USE THE app_context instead??
    app.config['RUN_SETUP'] = True                      # used in route '/' to see if this is the first time
    app.config['ASSISTANT'] = assistant                    # Current known assistant (should get from client)
    app.register_blueprint(start.bp)
    app.register_blueprint(message.msg)
    app.register_blueprint(assist.ap)

    with app.app_context():
        return app

