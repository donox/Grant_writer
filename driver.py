#!/usr/bin/env python3

import configparser
import datetime as dt
import os
# import shutil
import traceback
from pathlib import Path
from utilities.run_log_command import BasicLogger, list_files_in_directory
from assistant.grant_writer import GrantWriter   # , WriterAssistant
from assistant.io_manager import PrintAndSave
from assistant.vector_store_manager import VectorStoreManager
from assistant.file_manager import FileManager
from assistant.message_manager import Message
from ui_control.command_processor import Commands
from ui_control.client_interface import ClientInterface
from ui_client import create_app as app_ui
from openai import OpenAI

# from external_sites.manage_google_drive import ManageGoogleDrive


# RClone config file in /home/don/.config/rclone/rclone.conf

def driver():
    # This script runs daily
    do_testing = True

    # start_notest = dt.time(1, 0)     # but not if between 1am and 4am
    # end_notest = dt.time(4, 0)
    # if start_notest < dt.datetime.now().time() < end_notest:
    #     do_testing = False

    if do_testing:
        prototyping = False
        run_commands = True
        run_ui = False
    else:
        prototyping = False

    pth = os.path.abspath(os.curdir)            # Find current directory (where we are running)

    config = configparser.ConfigParser()

    with open("/home/don/PycharmProjects/grant_assistant/config_file.cfg") as source:
        config.read(source.name)
    # Load parameters from configuration file
    start_date = config['measurement period']['startDate']
    end_date = config['measurement period']['endDate']

    start_measurement = (dt.datetime.strptime(start_date, "%Y/%m/%d")).date()
    end_measurement = (dt.datetime.strptime(end_date, "%Y/%m/%d")).date()

    dbname = config['database']['dbName']
    dbuser = config['database']['dbUser']

    os.curdir = config['paths']['workingDirectory']         # Set current working directory
    work_directory = config['paths']['workingDirectory']
    logs_directory = config['paths']['logsDirectory']

    don_dir = Path('/home/don')                             # Don's home directory
    don_devel = don_dir / 'devel'                           # Development Directory (the '/' is a path join operator)

    # Linix commands to access Google Drive
    cmd_rclone = 'rclone -v copyto {} gdriveremote:/RClone/{}'
    # cmd_save_sst_files = "rclone -v copyto {} 'gdriveremote:/Sunnyside Times/SST Admin/{}'"
    # cmd_get_sst_files = "rclone -v copy 'gdriveremote:/Sunnyside Times/SST Admin/{}' {}"

    summary_logger = BasicLogger('summary_log', logs_directory)     # Logger - see use below
    summary_logger.make_info_entry('Start Summary Log')

    if run_ui:
        logger = BasicLogger('run_UI', logs_directory)
        target_directory = work_directory + 'worktemp/'
        try:
            flask_key = config['keys']['flaskKey']
            app = app_ui(flask_key)
            app.run(debug=True)

        except Exception as e:
            print(e)
            traceback.print_exc()
        logger.close_logger()
    if run_commands:
        logger = BasicLogger('run_commands', logs_directory)
        target_directory = work_directory + 'worktemp/'
        try:
            outfile = "/home/don/Documents/Temp/outfile.txt"
            cmd_path = '/home/don/PycharmProjects/grant_assistant/Temp/commands.json'
            handler = Commands(cmd_path, config, outfile)
            client_ui = ClientInterface(handler)
            flask_key = config['keys']['flaskKey']
            assistant = config['keys']['assistant']
            app = app_ui(flask_key, client_ui, assistant)
            app.run(debug=True)
            # handler.process_commands()

        except Exception as e:
            print(e)
            traceback.print_exc()
        logger.close_logger()


    if prototyping:
        logger = BasicLogger('prototyping', logs_directory)
        target_directory = work_directory + 'worktemp/'
        try:
            from practice_one import DoNothingWell
            message1 = None
            message2 = 37
            my_first_object = DoNothingWell(message1, message2)   # Do interesting stuff here
            my_first_object.print_something("A Message of Interest")
        except Exception as e:
            print(e)
            traceback.print_exc()
        logger.close_logger()

    summary_logger.make_info_entry('Summary Log Entries Completed')
    summary_logger.close_logger()


if __name__ == '__main__':
    driver()