from openai import OpenAI
from openai import AssistantEventHandler
from typing_extensions import override


class Assistant(object):
    assistant_count = 1

    def __init__(self, client, name=None, assistant_id=None):
        self.client = client
        self.name = name
        self.assistant = None
        self.id = assistant_id
        self.vector_stores = []   # List of vector_store_managers

        if self.id:
            try:
                self.assistant = self.client.beta.assistants.retrieve(self.id)
                self.name = self.assistant.name
            except Exception as e:
                print(f"Not Found: {self.id}")
        else:
            if not self.name:
                self.name = f"Assistant-{Assistant.assistant_count}"
                Assistant.assistant_count += 1
            self.assistant = self.client.beta.assistants.create(
                name=self.name,
                instructions=None,
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": []}},
                model="gpt-4o",
            )
            self.id = self.assistant.id

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def update_assistant(self, description=None, instructions=None, metadata=None, name=None,
                         response_format=None, temperature=None, tool_resources=None, tools=None, top_p=None, **kwargs):
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

    def add_vector_store(self, vector_store):
        """Add vector store to an assistant."""
        self.vector_stores.append(vector_store)
        vs_ids = [x.get_vector_store_id() for x in self.vector_stores]
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
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
