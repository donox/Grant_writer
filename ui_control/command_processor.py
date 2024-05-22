import json
from assistant.grant_writer import GrantWriter
from assistant.file_manager import FileManager
from assistant.vector_store_manager import VectorStoreManager
from assistant.io_manager import PrintAndSave


class Commands(object):
    def __init__(self, command_file_path, config, results_path, show_json=False):
        self.config = config
        self.command_file_path = command_file_path
        self.results_path = results_path
        self.show_json = show_json
        self.command_history = []
        self.stop_encountered = False
        self.supported_commands = {'stop': self.cmd_stop,
                                   'setup': self.cmd_setup,
                                   }
        self.grant_builder = None
        self.output_manager = None
        self.client = None  # OpenAI assistant
        self.vector_store_manager = None
        self.vector_store_list = []
        self.vector_store_id = None  # This is assuming there is only one VS in use
        self.assistant_id = None
        self.api_key = None

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
        self.assistant_id = self.config['keys']['assistant']
        self.api_key = self.config['keys']['openAIKey']

        self.grant_builder = GrantWriter(self.api_key, self.output_manager, self.assistant_id, self.vector_store_id,
                                         show_json=self.show_json)  # FIX SIGNATURE
        self.client = self.grant_builder.get_client()

        self.vector_store_manager = self.grant_builder.create_vector_store("VS1", vector_store_id=self.vector_store_id,
                                                                           show_json=self.show_json)
        self.vector_store_list = self.grant_builder.get_vector_stores()
        self.vector_store_id = self.vector_store_list[0].get_vector_store_id()  # assume there is a single VS in use.
