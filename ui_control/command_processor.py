import json
from assistant.grant_writer import GrantWriter
from assistant.file_manager import FileManager
from assistant.vector_store_manager import VectorStoreManager
from assistant.io_manager import PrintAndSave
from assistant.thread_manager import ThreadManager, Thread
from assistant.message_manager import Message
from assistant.assistant_manager import AssistantManager


class Commands(object):
    def __init__(self, command_file_path, config, results_path):
        self.config = config
        self.command_file_path = command_file_path
        self.results_path = results_path
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
                                   'cmd_update_message': self.cmd_update_message,
                                   'cmd_get_assistant_list': self.cmd_get_assistant_list,
                                   'cmd_add_new_assistant': self.cmd_add_new_assistant,
                                   'cmd_get_assistant_data': self.cmd_get_assistant_data,
                                   'cmd_update_assistant_instructions': self.cmd_update_assistant_instructions,
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

        self.vector_store_id = self.config['keys']['vectorStore']
        self.assistant_id = self.config['keys']['assistant']         # !!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.api_key = self.config['keys']['openAIKey']
        self.thread_path = self.config['paths']['threadList']     # We have to keep a list of known threads ourselves
        self.thread_manager = ThreadManager(self.thread_path)
        self.grant_builder = GrantWriter(self.api_key, self.output_manager, self.thread_manager, self.assistant_id, self.vector_store_id)
        self.assistant_manager = AssistantManager(self.grant_builder)
        self.assistant_manager.retrieve_existing_assistants()
        self.grant_builder.set_assistant_manager(self.assistant_manager)
        self.thread_manager.set_grant_builder(self.grant_builder)
        self.client = self.grant_builder.get_client()


        # this will look up an existing VS if given an id
        # TODO: there my be multiple vector stores
        self.vector_store_manager = self.grant_builder.create_vector_store("VS1",
                                                                           vector_store_id=self.vector_store_id)

    def cmd_get_user_threads(self, user):
        result = self.thread_manager.get_threads_for_user(user)
        return result

    def cmd_update_assistant(self, cmd_dict):
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

    def cmd_run_query(self, user, thread_name, assistant):
        if self.grant_builder.create_run(user, thread_name, assistant):   # not False if run completed
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

    def cmd_get_thread_list(self, user):
        result = self.grant_builder.get_thread_list_user(user)
        return result

    def cmd_add_new_thread(self, data):
        result = self.grant_builder.add_new_thread(data)
        return result

    def cmd_get_assistant_list(self):
        result = self.assistant_manager.get_assistants_as_list_of_dictionaries()
        return result

    def cmd_add_new_assistant(self, data):
        result = self.grant_builder.add_new_assistant(data)
        return result

    def cmd_get_assistant_data(self, assistant_id):
        result = self.assistant_manager.get_assistant_data(assistant_id)
        return result

    def cmd_create_run(self, user, name, assistant_id):           # IS THIS RIGHT, Can it be deleted?
        result = self.grant_builder.create_run(user, name, assistant_id)
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

    def cmd_delete_thread(self, thread_name):
        result = self.grant_builder.delete_thread(thread_name)
        return result

    def cmd_delete_assistant(self, assistant_id):
        result = self.assistant_manager.delete_assistant(assistant_id)
        return result

    def cmd_update_assistant_instructions(self, assistant_id, instructions):
        assistant = self.assistant_manager.get_assistant_from_id(assistant_id)
        result = assistant.update_assistant(instructions=instructions)
        return result


