#!/usr/bin/env python3

import configparser
from ui_control.command_processor import Commands
from ui_control.client_interface import ClientInterface
from ui_client import create_app as app_ui

config = configparser.ConfigParser()

with open("/home/don/PycharmProjects/grant_assistant/config_file.cfg") as source:
    config.read(source.name)

def create_app():
    cmd_path = '/home/don/PycharmProjects/grant_assistant/Temp/commands.json'
    outfile = "/home/don/Documents/Temp/outfile.txt"
    handler = Commands(cmd_path, config, outfile)
    client_ui = ClientInterface(handler)
    flask_key = config['keys']['flaskKey']
    assistant = config['keys']['assistant']
    app = app_ui(flask_key, client_ui, assistant)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)