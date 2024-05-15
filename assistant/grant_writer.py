from openai import OpenAI
from openai import AssistantEventHandler
from typing_extensions import override

assistant_instructions = """Attempt to fill out the Letter of Intent (LOI) using information from the vector store 
wherever possibly.  Where you are unable to determine an appropriate response, insert a note enclosed in angle brackets 
indicating that you could not develop the response and, if possible, why not.  Do not guess or make up facts not in 
evidence."""



class GrantWriter(object):
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.vector_stores = []
        self.assistant = self.client.beta.assistants.create(
            name="Grant Writer",
            instructions=assistant_instructions,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": []}},
            model="gpt-4o",
        )
        self.thread = self.client.beta.threads.create()
        self.test_file = self.client.files.create(file=open("/home/don/Documents/Wonders/test forms/Kronkosky - LOI.docx", "rb"),
                                        purpose="assistants")
        self.message = self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content="Fill out the LOI in the associated file using information from the vector store",
            attachments=[{"file_id": self.test_file.id,
                          "tools": [{"type": "file_search"}]}]
        )
        # self.message2 = self.client.beta.threads.messages.create(
        #     thread_id=self.thread.id,
        #     role="user",
        #     content="What are the expenses for Wonders and Worries in 2023?  The necessary data is in the vector store."
        # )

    def run_assistant(self):
        # Then, we use the `stream` SDK helper
        # with the `EventHandler` class to create the Run
        # and stream the response.
        # print(f"AT RUN - Assistant ID: {self.assistant.id}")
        with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
                # instructions="Display the answers with the numbers written out",
                event_handler=EventHandler(),
        ) as stream:
            stream.until_done()

    def add_vector_store(self, vector_store_id):
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
        )
        # self.vector_stores.append(vector_store_id)
        # print(f"AT ADD - Assistant ID: {self.assistant.id}")
        # print(f"VS: {vector_store_id}, {self.vector_stores}")

    def get_client(self):
        return self.client


class EventHandler(AssistantEventHandler):
    """    # First, we create a EventHandler class to define
    # how we want to handle the events in the response stream."""

    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


class MakeVectorStore(object):
    def __init__(self, client, name):
        self.client = client
        self.store_name = name
        self.vector_store = client.beta.vector_stores.create(name=name)

    def make_store(self, file_list):
        file_streams = [open(path, "rb") for path in file_list]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store.id, files=file_streams
        )
        return file_batch
