from openai import OpenAI
from openai import AssistantEventHandler
from typing_extensions import override
from db_management.db_manager import DatabaseManager, DBAssistant
from pathlib import Path
import json


class AssistantManager(object):
    def __init__(self, grant_builder):
        self.grant_builder = grant_builder
        self.client = self.grant_builder.get_client()  # OAI c
        self.known_assistants = []   # Not OAI assistants

    def create_assistant(self, name):
        assistant = Assistant(self.grant_builder, name=name)
        self.known_assistants.append(assistant)

    def retrieve_existing_assistants(self):
        self.known_assistants = []
        assistant_list = self.client.beta.assistants.list()
        for assistant in assistant_list:
            mgr = Assistant(self.client, assistant_id=assistant.id)
            self.known_assistants.append(mgr)

    def get_assistants_list(self):
        return self.retrieve_existing_assistants()

    def get_objects_list(self):  # Support for generic list
        return self.get_assistants_list()

    def get_assistants_as_list_of_dictionaries(self):
        result = []
        for assistant in self.known_assistants:
            result.append({"name": assistant.get_name(),
                           "id": assistant.get_id()})
        return result

    def get_assistant_from_id(self, assistant_id):
        res = [x for x in self.known_assistants if x.get_id() == assistant_id]
        if res:
            return res[0]
        else:
            return None

    def get_object_by_id(self, object_id):
        return self.get_assistant_from_id(object_id)

    def get_assistant_data(self, assistant_id):
        assistant = self.get_assistant_from_id(assistant_id)
        return assistant.get_content_data()

    def update_object_details(self, obj_id, data):
        asst = self.get_assistant_from_id(obj_id)
        res = asst.update_assistant(**data)
        return res

    def delete_assistant(self, assistant_id):
        this_assistant = None
        for x in self.known_assistants:
            if x.get_id() == assistant_id:
                this_assistant = x
        if not this_assistant:
            print(f"Assistant {assistant_id} was not found getting error")
            return False
        try:
            result = self.client.beta.assistants.delete(this_assistant.get_id())
        except Exception as e:  # openAI - NotFoundError
            print(f"Assistant {assistant_id} was not found getting error {e.args}")
            return False
        if result.deleted:
            self.known_assistants.remove(this_assistant)
            this_assistant = None
        return result.deleted  # True/False


class Assistant(object):
    def __init__(self, client, name=None, assistant_id=None):
        self.client = client
        self.name = name
        self.oai_assistant = None
        self.id = assistant_id
        self.vector_stores = []  # List of vector_store_managers
        self.uploaded_files = []

        if self.id:
            try:
                self.oai_assistant = self.client.beta.assistants.retrieve(self.id)
                self.name = self.oai_assistant.name
            except Exception as e:
                print(f"Not Found: {self.id}")
        else:
            self.oai_assistant = self.client.beta.assistants.create(
                name=self.name,
                instructions=None,
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": []}},
                model="gpt-4o",
            )
            self.id = self.oai_assistant.id

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_oai_assistant(self):
        return self.oai_assistant

    def get_content_data(self):
        res = json.loads(self.oai_assistant.to_json())
        return res

    def update_assistant(self, description=None, instructions=None, metadata=None, name=None,
                         response_format=None, temperature=None, tool_resources=None, tools=None, top_p=None, **kwargs):
        params = {"assistant_id": self.oai_assistant.id}
        if description:
            params["description"] = description
        if instructions:
            params["instructions"] = instructions
        if metadata:
            params["metadata"] = metadata
        if name:
            params["name"] = name
        if response_format:
            params["response_format"] = response_format
        if temperature:
            params["temperature"] = temperature
        if tool_resources:
            params["tool_resources"] = tool_resources
        if tools:
            params["tools"] = tools
        if top_p:
            params["top_p"] = top_p
        try:
            self.oai_assistant = self.client.beta.assistants.update(**params)
        except Exception as e:
            print(f"Failure updating assistant: {e.args}")
            return False
        return True

    def add_vector_store(self, vector_store):
        """Add vector store to an assistant."""
        self.vector_stores.append(vector_store)
        vs_ids = [x.get_vector_store_id() for x in self.vector_stores]
        self.oai_assistant = self.client.beta.assistants.update(
            assistant_id=self.oai_assistant.id,
            tool_resources={"file_search": {"vector_store_ids": vs_ids}}
        )

    def run_assistant(self, thread, output_mgr):
        # Then, we use the `stream` SDK helper
        # with the `EventHandler` class to create the Run
        # and stream the response.
        with self.client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id=self.id,
                event_handler=EventHandler(output_mgr),
        ) as stream:
            stream.until_done()

    def attach_file(self, path):
        # Attach file to current assistant.
        with open(path, 'rb') as upload_file:
            try:
                file = self.client.files.create(
                    file=upload_file,
                    purpose="assistants",
                )
                file_id = file.id
                # APPARENTLY NEED TO USE VECTOR STORE.  CAN'T ADD FILES JUST TO THE ASSISTANT (ANYMORE?)
                # https://community.openai.com/t/confusion-with-the-vector-storage-option-when-searching-for-files/721083
                response = self.client.beta.assistants.update(
                    assistant_id=self.id,
                    tools=[
                        {"type": "file_search",
                         "file_id": file_id}
                    ],
                    model="gpt-4o"
                )
                self.uploaded_files.append(path)   #openAI file object
            except Exception as e:
                return False
        return True

    def to_json(self):
        return json.loads(self.oai_assistant.to_json())


class EventHandler(AssistantEventHandler):
    """    # First, we create a EventHandler class to define
    # how we want to handle the events in the response stream."""

    def __init__(self, output_manager):
        self.output_manager = output_manager
        super().__init__()

    @override
    def on_text_created(self, text) -> None:
        out_string = "\nassistant > "
        # print(out_string, end="", flush=True)
        self.output_manager.output(out_string, end="")

    @override
    def on_text_delta(self, delta, snapshot):
        # print(delta.value, end="", flush=True)
        self.output_manager.output(delta.value, end="")

    def on_tool_call_created(self, tool_call):
        out_string = f"\nassistant > {tool_call.type}\n"
        # print(f"\nassistant > {tool_call.type}\n", flush=True)
        self.output_manager.output(out_string)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                # print(delta.code_interpreter.input, end="", flush=True)
                self.output_manager.output(delta.code_interpreter.input, end="")
            if delta.code_interpreter.outputs:
                # print(f"\n\noutput >", flush=True)
                self.output_manager.output(f"\n\noutput >")
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        # print(f"\n{output.logs}", flush=True)
                        self.output_manager(f"\n{output.logs}")
