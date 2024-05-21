#!/usr/bin/env python3

import configparser
import datetime as dt
import os
# import shutil
import traceback
from pathlib import Path
from utilities.run_log_command import BasicLogger, list_files_in_directory
from assistant.grant_writer import GrantWriter, WriterAssistant
from assistant.io_manager import PrintAndSave
from assistant.vector_store_manager import VectorStoreManager
from assistant.file_manager import FileManager
from assistant.message_manager import MessageManager

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
        write_grants = True
    else:
        prototyping = False
        write_grants = False

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

    if write_grants:
        logger = BasicLogger('prototyping', logs_directory)
        target_directory = work_directory + 'worktemp/'
        try:
            outfile = "/home/don/Documents/Temp/outfile.txt"
            output_mgr = PrintAndSave(outfile, True)

            vector_store_id = config['keys']['vectorStore']
            assistant_id = config['keys']['assistant']
            api_key = config['keys']['openAIKey']

            # assistant_id = None
            assistant_instructions = """Attempt to fill out the Letter of Intent (LOI) using information from the vector store
            wherever possibly.  Where you are unable to determine an appropriate response, insert a note enclosed in angle brackets
            indicating that you could not develop the response and, if possible, why not.  Do not guess or make up facts not in
            evidence."""
            assistant_instructions = """Use an informal voice. """

            # USE ChatCompletion API
            # builder = WriterAssistant("My Assistent", api_key)
            # thread_id = builder.get_thread_id()
            # out_message = builder.get_response(thread_id, "Do Something")

            #USE Assistants API
            show_json = True
            grant_builder = GrantWriter(api_key, output_mgr, assistant_id, vector_store_id, show_json=show_json)    # FIX SIGNATURE
            cl = grant_builder.get_client()

            # create/use file manager
            # file_obj = FileManager(cl)
            # file_obj.attach_file("/home/don/PycharmProjects/grant_assistant/body_of_knowledge/Annual Data/Program Report FY 2023.docx",
            #                      "assistants")
            # file_obj.pass_file_to_thread(grant_builder.get_thread().id)

            vs = grant_builder.get_vector_stores()
            vector_store_id = vs[0].id   # we will assume there is a single VS in use.
            vs_mgr = VectorStoreManager(cl, None, vs_id=vector_store_id, show_json=show_json)
            file_list = list_files_in_directory("/home/don/PycharmProjects/grant_assistant/body_of_knowledge")
            vs_mgr.add_files_to_store(file_list)

            grant_builder.update_assistant(instructions=assistant_instructions,
                                           tools=[{"type": "file_search"}],
                                           tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
                                           )

            # message = MessageManager(cl, grant_builder.get_thread())
            # content = "Fill out the LOI in the associated file using information from the vector store"
            # message.add_content(content, "user")
            # message.add_file_attachment("/home/don/Documents/Wonders/test forms/Kronkosky - LOI.docx")
            # message.create_message()

            grant_builder.run_assistant()
            output_mgr.close()
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