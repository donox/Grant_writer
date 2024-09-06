import json
from assistant.grant_writer import GrantWriter
from assistant.file_manager import FileManager
from assistant.vector_store_manager import VectorStoreManager
from assistant.io_manager import PrintAndSave
from assistant.thread_manager import ThreadManager, Thread
from assistant.message_manager import Message
from assistant.assistant_manager import AssistantManager
from ui_client.routes.generics import get_object_from_id_kernel, get_object_from_name_kernel, check_setup
from flask import current_app
from db_management.db_manager import DatabaseManager


class Commands(object):
    def __init__(self, command_file_path, config, results_path):
        self.config = config
        self.command_file_path = command_file_path
        self.results_path = results_path
        self.db_path = self.config['paths']['dbSQLlite']
        self.db_processor = None
        self.command_history = []
        self.stop_encountered = False
        self.supported_commands = {'stop': self.cmd_stop,
                                   'setup': self.cmd_setup,
                                   'update_assistant': self.cmd_update_assistant,
                                   "attach_file_to_assistant": self.cmd_attach_file_to_assistant,
                                   # "add_message": self.cmd_add_message,    # USE cmd_add_message below???
                                   "run_query": self.cmd_run_query,
                                   # "get_message_list": self.cmd_get_message_list,
                                   "get_last_results": self.cmd_get_last_results,
                                   "get_text_responses": self.cmd_get_text_responses,
                                   "cmd_get_thread_list": self.cmd_get_thread_list,
                                   "cmd_add_new_thread": self.cmd_add_new_thread,
                                   "cmd_create_run": self.cmd_create_run,
                                   "cmd_add_message": self.cmd_add_message,
                                   "cmd_delete_thread": self.cmd_delete_thread,
                                   "cmd_delete_store": self.cmd_delete_store,
                                   "cmd_delete_assistant": self.cmd_delete_assistant,
                                   'cmd_update_message': self.cmd_update_message,
                                   'cmd_get_assistant_list': self.cmd_get_assistant_list,
                                   'cmd_add_new_assistant': self.cmd_add_new_assistant,
                                   'cmd_get_assistant_data': self.cmd_get_assistant_data,
                                   'cmd_get_store_data': self.cmd_get_store_data,
                                   'cmd_update_assistant_instructions': self.cmd_update_assistant_instructions,
                                   'cmd_make_thread_json': self.cmd_make_thread_json,
                                   'cmd_get_assistant_from_id': self.cmd_get_assistant_from_id,
                                   'cmd_get_object_from_id': self.cmd_get_object_from_id,
                                   }
        self.grant_builder = None
        self.assistant_manager = None
        self.output_manager = None
        self.client = None  # OpenAI assistant
        self.file_manager = None
        self.vector_store_manager = None
        self.vector_store_list = []
        self.vector_store_id = None  # This is assuming there is only one VS in use
        self.assistant_id = None
        self.api_key = None
        self.thread_path = None
        self.thread_manager = None

    def read_command(self):
        with open(self.command_file_path, 'r') as cmdfile:
            try:
                data = json.load(cmdfile)
            except Exception as e:
                print(f'Command Read Fail: {e.args}')
                return None
            self.command_history.append(data)
            return data

    def process_commands(self):
        while not self.stop_encountered:
            cmds = self.read_command()
            if type(cmds) is list:
                for cmd in cmds:
                    self.process_single_command(cmd)
            else:
                self.process_single_command(cmds)

    def process_single_command(self, cmd_dict):
        try:
            cmd = cmd_dict['command'].lower()
            self.supported_commands[cmd](cmd_dict)

        except Exception as e:
            print(f"Command not found: {e.args}")

    def cmd_stop(self, cmd_dict):
        self.stop_encountered = True

    def cmd_setup(self, cmd_dict):
        self.output_manager = PrintAndSave(self.results_path, True)
        self.api_key = self.config['keys']['openAIKey']

        # DELETE NEXT WHEN DB WORKING
        self.thread_path = self.config['paths']['threadList']     # We have to keep a list of known threads ourselves

        self.thread_manager = ThreadManager(self.db_path)
        self.grant_builder = GrantWriter(self.api_key, self.output_manager, self.thread_manager)
        self.client = self.grant_builder.get_client()

        self.thread_manager.set_grant_builder(self.grant_builder)
        self.thread_manager.complete_thread_creation()
        current_app.config['THREAD_MANAGER'] = self.thread_manager

        self.assistant_manager = AssistantManager(self.grant_builder)
        self.assistant_manager.retrieve_existing_assistants()
        self.grant_builder.set_assistant_manager(self.assistant_manager)
        current_app.config['ASSISTANT_MANAGER'] = self.assistant_manager

        self.vector_store_manager = VectorStoreManager(self.client)
        current_app.config['STORE_MANAGER'] = self.vector_store_manager

        # t1 = {'id': 'thread_WNzhwb6RaEn0ufslZlxafJ82', 'name': 'TestWW', 'owner': 'don', 'purpose': 'Explore WW work'}
        # t2 = {'id': 'thread_0tvkRE6OulYRqRlS4tLue9ik', 'name': 'jstest9', 'owner': 'don', 'purpose': 'test'}
        # t3 = {'id': 'thread_1kXdtJrhwHZknixfBlllR3CO', 'name': 'Test Thread 936', 'owner': 'don', 'purpose': 'Testing thread operations'}
        # self.thread_manager.add_preexisting_thread(t1)
        # self.thread_manager.add_preexisting_thread(t2)
        # self.thread_manager.add_preexisting_thread(t3)

    @staticmethod
    def cmd_get_object_from_id(list_type, obj_id):
        print(f" COMMAND PROCESSOR: List Type: {list_type}, ID: {obj_id}", flush=True)
        result = get_object_from_id_kernel(list_type, obj_id)
        return result

    @staticmethod
    def cmd_get_object_from_name(list_type, obj_name):
        print(f" COMMAND PROCESSOR: List Type: {list_type}, name: {obj_name}", flush=True)
        result = get_object_from_name_kernel(list_type, obj_name)
        return result

    def cmd_make_thread_json(self, thread_name):
        thread = self.thread_manager.get_known_thread_entry_from_name(thread_name)
        result = thread.make_thread_jstree_json()
        return result

    def cmd_get_user_threads(self, user):
        check_setup()
        result = self.thread_manager.get_threads_for_user(user)
        return result

    def cmd_get_assistant_from_id(self, assistant_id):
        result = self.assistant_manager.get_assistant_from_id(assistant_id)
        return result

    def cmd_update_assistant(self, cmd_dict):
        check_setup()
        self.grant_builder.update_assistant(**cmd_dict)

    def cmd_attach_file_to_assistant(self, cmd_dict):
        try:
            if not self.file_manager:
                self.file_manager = FileManager(self.client)
            purpose = cmd_dict['purpose']
            if purpose == 'user':
                purpose = 'user_data'
            self.file_manager.attach_file(cmd_dict['file_path'], purpose)
            self.file_manager.pass_file_to_thread(self.grant_builder.get_thread().id)
        except Exception as e:
            print(f"error in file attachment: {e.args}")

    def cmd_run_query(self, owner, thread_name, assistant):
        if self.grant_builder.create_run(owner, thread_name, assistant):   # not False if run completed
            thread = self.thread_manager.get_known_thread_entry_from_name(thread_name)
            thread.update_messages()

    # def cmd_get_message_list(self, thread_id):              # DEAD
    #     result = self.grant_builder.get_messages(thread_id)
    #     return result

    def cmd_get_text_responses(self, user, thread_name, assistant_id):
        msg_mgrs = self.cmd_get_last_results(user, thread_name, assistant_id)
        response = ""
        for mgr in msg_mgrs:
            response += mgr.create_response_text() + "\n"
        return response

    def cmd_get_thread_list(self):
        result = self.thread_manager.get_thread_list()
        return result

    def cmd_add_new_thread(self, data):
        result = self.thread_manager.add_new_thread(data)
        return result

    def cmd_get_assistant_list(self):
        result = self.assistant_manager.get_assistants_as_list_of_dictionaries()
        return result

    def cmd_add_new_assistant(self, data):
        result = self.grant_builder.add_new_assistant(data)
        self.assistant_manager.retrieve_existing_assistants()
        return result

    def cmd_get_vector_store_list(self):
        result = self.vector_store_manager.get_vector_stores_as_list_of_dictionaries()
        return result

    def cmd_add_new_vector_store(self, data):
        result = self.vector_store_manager.add_new_vector_store(data['name'])
        self.vector_store_manager.update_existing_vector_stores()
        return result

    def cmd_get_assistant_data(self, assistant_id):
        result = self.assistant_manager.get_assistant_data(assistant_id)
        return result

    def cmd_get_store_data(self, store_id):
        vs = self.vector_store_manager.get_vector_store_by_id(store_id)
        if vs:
            result = vs.get_content_data()
            return result
        else:
            return None

    def cmd_create_run(self, owner, name, assistant_id):           # IS THIS RIGHT, Can it be deleted?
        result = self.grant_builder.create_run(owner, name, assistant_id)
        return result

    def cmd_add_message(self, cmd):
        # cmd = {"command": "add_message", "content": message, "role": "user", "thread_name": thread_name,
        # "assistant": assistant}
        thread = self.thread_manager.get_known_thread_entry_from_name(cmd["thread_name"])
        if not thread:
            return False            # return a message or something???
        message = Message(self.grant_builder, thread)
        # TODO:  Any file attachments must be added before this call
        message.add_content_and_create_message_in_thread(cmd['content'], cmd['role'])
        return message

    def cmd_update_message(self, message_id, role, thread_name, content):
        result = self.grant_builder.update_message(message_id, role, thread_name, content)
        return result

    def cmd_get_thread_messages(self, thread_name):
        """Retrieve list of dictionaries representing messages from the last query run."""
        if not self.grant_builder:
            foo = 3
        thread = self.grant_builder.get_thread_by_name(thread_name)
        thread.update_messages()
        result = thread.get_most_recent_responses()
        return result

    def cmd_get_last_results(self, user, thread_name, assistant_id):
        thread = self.thread_manager.get_known_thread_entry_from_name(thread_name)
        result = thread.get_most_recent_responses()
        if result is None or result is []:
            return "There were no results to return"
        return result

    def cmd_delete_thread(self, thread_id):
        check_setup()
        result = self.grant_builder.delete_thread(thread_id)
        return result

    def cmd_delete_assistant(self, assistant_id):
        check_setup()
        result = self.assistant_manager.delete_assistant(assistant_id)
        return result

    def cmd_delete_store(self, store_id):
        check_setup()
        result = self.vector_store_manager.delete_store(store_id)
        return result

    def cmd_update_assistant_instructions(self, assistant_id, instructions):
        assistant = self.assistant_manager.get_assistant_from_id(assistant_id)
        result = assistant.update_assistant(instructions=instructions)
        return result

    def cmd_attach_file(self, assistant_id, file_path):
        assistant = self.assistant_manager.get_assistant_from_id(assistant_id)
        result = assistant.attach_file(path=file_path)
        return result

