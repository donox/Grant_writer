from openai import OpenAI
from openai import AssistantEventHandler
from typing_extensions import override


class GrantWriter(object):
    def __init__(self, api_key, output_mgr, assistant_id=None, vector_store_id=None):
        self.client = OpenAI(api_key=api_key)
        self.output_mgr = output_mgr
        self.vector_store_list = []
        if assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(assistant_id)
        else:
            self.assistant = self.client.beta.assistants.create(
                name="Grant Writer",
                # instructions=assistant_instructions,
                # tools=[{"type": "file_search"}],
                # tool_resources={"file_search": {"vector_store_ids": []}},
                model="gpt-4o",
            )
        if vector_store_id:
            vs = self.client.beta.vector_stores.retrieve(vector_store_id)
        else:
            vs = self.create_vector_store("VS"+str(len(self.vector_store_list)))
        self.vector_store_list.append(vs)
        self.thread = self.client.beta.threads.create()
        # self.test_file = self.client.files.create(file=open("/home/don/Documents/Wonders/test forms/Kronkosky - LOI.docx", "rb"),
        #                                 purpose="assistants")
        # self.message = self.client.beta.threads.messages.create(
        #     thread_id=self.thread.id,
        #     role="user",
        #     content="Fill out the LOI in the associated file using information from the vector store",
        #     attachments=[{"file_id": self.test_file.id,
        #                   "tools": [{"type": "file_search"}]}]
        # )
        # # self.message2 = self.client.beta.threads.messages.create(
        # #     thread_id=self.thread.id,
        # #     role="user",
        # #     content="What are the expenses for in 2023?  The necessary data is in the vector store."
        # # )

    def create_vector_store(self, name):
        vs = self.client.beta.vector_stores.create(name=name)
        self.vector_store_list.append(vs)
        return vs

    def add_vector_store(self, vector_store_id):
        """Add vector store to an assistant."""
        # Note the assumption that the assistant has only this one store!!!!!!!!!!!
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
        )
        # self.vector_stores.append(vector_store_id)
        # print(f"AT ADD - Assistant ID: {self.assistant.id}")
        # print(f"VS: {vector_store_id}, {self.vector_stores}")

    def update_assistant(self, description=None, instructions=None, metadata=None, name=None,
                         response_format=None, temperature=None, tool_resources=None, tools=None, top_p=None):
        params = {"assistant_id": self.assistant.id}
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
        self.assistant = self.client.beta.assistants.update(**params)

    def run_assistant(self):
        # Then, we use the `stream` SDK helper
        # with the `EventHandler` class to create the Run
        # and stream the response.
        with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                # instructions="Display the answers with the numbers written out",
                event_handler=EventHandler(self.output_mgr),
        ) as stream:
            stream.until_done()

    def get_client(self):
        return self.client

    def get_vector_stores(self):
        return self.vector_store_list

    def get_thread(self):
        return self.thread


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



