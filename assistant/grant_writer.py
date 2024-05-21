from openai import OpenAI, ChatCompletion
from openai import AssistantEventHandler
from typing_extensions import override


class GrantWriter(object):
    def __init__(self, api_key, output_mgr, assistant_id=None, instructions=None, vector_store_id=None, show_json=False):
        self.show_json = show_json
        self.client = OpenAI(api_key=api_key)
        self.output_mgr = output_mgr
        self.vector_store_list = []
        if assistant_id:
            self.assistant = self.client.beta.assistants.retrieve(assistant_id)
        else:
            self.assistant = self.client.beta.assistants.create(
                name="Grant Writer",
                instructions=instructions,
                tools=[{"type": "file_search"}],
                tool_resources={"file_search": {"vector_store_ids": []}},
                model="gpt-4o",
            )
        if self.show_json:
            self.output_mgr.output_json(self.assistant.model_dump_json(), end="", header="Initial Assistant")

        if vector_store_id:
            vs = self.client.beta.vector_stores.retrieve(vector_store_id)
        else:
            vs = self.create_vector_store("VS"+str(len(self.vector_store_list)))
        self.vector_store_list.append(vs)
        if show_json:
            self.output_mgr.output_json(vs.model_dump_json(), header="Initial Vector Store")
        self.thread = self.client.beta.threads.create()
        self.test_file = self.client.files.create(file=open("/home/don/Documents/Wonders/test forms/Kronkosky - LOI.docx", "rb"),
                                                  purpose="assistants")
        self.message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content="What cities have offices?",
            attachments=[{"file_id": self.test_file.id,
                          "tools": [{"type": "file_search"}]}]
        )
        if show_json:
            self.output_mgr.output_json(self.message.model_dump_json(), header="Message: 1")
        #  URL's being used to try to get this to work!!
        #  https://github.com/openai/openai-python/blob/main/src/openai/resources/beta/threads/threads.py
        #  https://platform.openai.com/docs/assistants/tools/file-search
        #  https://platform.openai.com/assistants

        self.message2 = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content="What are the expenses for in 2023?  The necessary data is in the vector store."
        )
        if show_json:
            self.output_mgr.output_json(self.message.model_dump_json(), header="Message: 2")
        if show_json:
            self.output_mgr.output_json(self.thread.model_dump_json(), header="Thread After Message Create")

    def create_vector_store(self, name, show_json=False):
        vs = self.client.beta.vector_stores.create(name=name)
        self.vector_store_list.append(vs)
        if show_json:
            self.output_mgr.output_json(vs.model_dump_json())
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
        if self.show_json:
            self.output_mgr.output_json(self.assistant.model_dump_json(), header="UPDATE Assistant", end="")

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
        if self.show_json:
            self.output_mgr.output(f"RESULT after run with thread_id: {self.thread.id}\n", end="")
            ml = self.client.beta.threads.messages.list(thread_id=self.thread.id)
            for nbr, msg in enumerate(ml.data):
                self.output_mgr.output_json(msg.model_dump_json(), header=f"MSG: {nbr} ", end="")

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


class WriterAssistant(object):
    def __init__(self, name, api_key, thread_id=None):
        self.name = name
        self.client = OpenAI(api_key=api_key)
        if thread_id:
            self.thread_id = thread_id
        else:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
        self.conversation_threads = {}

    def upload_file(self, file_path):
        with open(file_path, 'rb') as file:
            response = self.client.files.create(file=file, purpose='answers')
        return response['id']

    def get_response(self, thread_id, user_message, file_id=None):
        if thread_id not in self.conversation_threads:
            self.conversation_threads[thread_id] = [
                {"role": "system", "content": "You are an assistant."}
            ]

        # Add user message to the history of the specific thread
        self.conversation_threads[thread_id].append({"role": "user", "content": user_message})

        # If there's a file associated, include it in the context
        if file_id:
            self.conversation_threads[thread_id].append({"role": "system", "content": f"File ID: {file_id}"})

        # Send the conversation history to the API
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=self.conversation_threads[thread_id]
        )

        # Extract assistant's message from the response
        # message.content, message.role, message.function_call, message.tool_calls
        assistant_message = response.choices[0].message.content

        # Add assistant's message to the history
        self.conversation_threads[thread_id].append({"role": "assistant", "content": assistant_message})

        return assistant_message

    def get_thread_id(self):
        return self.thread_id



