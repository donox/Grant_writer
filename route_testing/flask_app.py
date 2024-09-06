#!/usr/bin/env python3

import configparser
from ui_control.command_processor import Commands
from ui_control.client_interface import ClientInterface
from ui_client import create_app as app_ui

config = configparser.ConfigParser()

with open("/home/don/PycharmProjects/grant_assistant/config_file.cfg") as source:
    config.read(source.name)


def create_app():
    print(f"USING flask_app.py - is this the preferred startup????")
    cmd_path = '/home/don/PycharmProjects/grant_assistant/Temp/commands.json'
    outfile = "/home/don/Documents/Temp/outfile.txt"
    handler = Commands(cmd_path, config, outfile)
    client_ui = ClientInterface(handler)
    flask_key = config['keys']['flaskKey']
    assistant = config['keys']['assistant']
    path_to_db = config['paths']['dbSQLlite']
    app = app_ui(flask_key, client_ui, assistant, path_to_db)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)