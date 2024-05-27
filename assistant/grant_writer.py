from typing import List, Any

from openai import OpenAI, ChatCompletion
from openai import AssistantEventHandler
from typing_extensions import override
from assistant.vector_store_manager import VectorStoreManager, get_known_vector_stores
from assistant.message_manager import MessageManager


#  URL's  used to try to get this to work!!
#  https://github.com/openai/openai-python/blob/main/src/openai/resources/beta/threads/threads.py
#  https://platform.openai.com/docs/assistants/tools/file-search
#  https://platform.openai.com/assistants

class GrantWriter(object):
    def __init__(self, api_key, output_mgr, assistant_id=None, instructions=None, vector_store_id=None,
                 show_json=False):
        self.show_json = show_json
        self.client = OpenAI(api_key=api_key)
        self.output_mgr = output_mgr
        self.vector_store_list = []  # list of vector_store_manager objects that have been instantiated
        self.message_list = []
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

        # if vector_store_id:
        #     vs = self.client.beta.vector_stores.retrieve(vector_store_id)
        # else:
        #     vs = self.create_vector_store("VS" + str(len(self.vector_store_list)))
        # self.vector_store_list.append(vs)
        # if show_json:
        #     self.output_mgr.output_json(vs.get_vector_store_object().model_dump_json(), header="Initial Vector Store")
        self.thread = self.client.beta.threads.create()
        # self.test_file = self.client.files.create(file=open("/home/don/Documents/Wonders/test forms/Kronkosky - LOI.docx", "rb"),
        #                                           purpose="assistants")

    def create_vector_store(self, name, vector_store_id=None, show_json=False):
        vs = VectorStoreManager(self.client, name, vs_id=vector_store_id, show_json=show_json)
        self.vector_store_list.append(vs)
        if show_json:
            self.output_mgr.output_json(vs.get_vector_store_object().model_dump_json())
        return vs

    def add_vector_store(self, vector_store_id):
        """Add vector store to an assistant."""
        # Note the assumption that the assistant has only this one store!!!!!!!!!!!
        self.assistant = self.client.beta.assistants.update(
            assistant_id=self.assistant.id,
            tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}}
        )

    def add_message(self, role, content, add_file_path=None):
        msg = MessageManager(self.client, self.thread)
        msg.add_content(content, role)
        if add_file_path:
            msg.add_file_attachment(add_file_path)
        msg_obj = msg.create_message()
        self.message_list.append(msg)       # add MessageManager object
        if self.show_json:
            self.output_mgr.output_json(msg_obj.model_dump_json(), header="Message: 1")    # HEader???
        return msg

    def get_messages(self, thread_id):
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        # Check if we are maintaining list of MessageManagers equal to message list from API
        # If not, we have a leak of some sort.
        thread_messages: list[Any] = [x for x in self.message_list if x.get_thread_id() == thread_id]
        # if len(messages.data) != len(thread_messages):            #  THIS COMPARES messages to MessageManagers!!!
        #     message_ids = [x.get_message_id() for x in thread_messages]
        #     api_message_ids = [x.id for x in messages.data]
        #     # produce list of messages that are missing in one of the input lists
        #     compared_result = [x for x in message_ids + api_message_ids if x not in message_ids or
        #                        x not in api_message_ids]
        #     foo = 3
        #     raise ValueError(f"Message lists out of sync.  {compared_result} is missing in an input list")
        return thread_messages

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
        if self.show_json:
            self.output_mgr.output_json(self.assistant.model_dump_json(), header="UPDATE Assistant", end="")

    def run_assistant(self):
        # Then, we use the `stream` SDK helper
        # with the `EventHandler` class to create the Run
        # and stream the response.
        with self.client.beta.threads.runs.stream(
                thread_id=self.thread.id,                       # TODO: address multiple threads
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

    def update_message_lists(self, thread_id):
        """Update and verify message lists for specific thread.

        Presume messages for a thread are not significantly long (performance issues) and assume that
            update_message_lists is called at least once for each non-assistant message.
            -Create sets of message id's corresponding to all messages in thread and another from self.message_list.
            -Verify there are no messages in self.message_list that are not in those from api.
            -Remove all from api list that exist in self.message_list.
            -Remaining list should all be responses (role: assistant) for last message in self.message_list.
            -Add responses to most recent user/system message.  Most recent should be first in decimated list.  Add
                to MessageManger in reverse order.
        """
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        thread_ids = set()
        for msg in messages:
            thread_ids.add(msg.id)
        existing_ids = set()
        for msg in self.message_list:
            existing_ids.add(msg.get_message_id())
            for msg_id in msg.get_response_ids():
                existing_ids.add(msg_id)
        x = existing_ids.difference(thread_ids)
        if x:
            print(f"Messages found not in current thread: {x}")
            raise SystemError(f"Messages found not in current thread: {x}")
        y = thread_ids.difference(existing_ids)
        add_list = [z for z in thread_ids if z in y]
        add_list.reverse()
        last_msg_mgr = self.message_list[-1]
        # print(f"query: {last_msg_mgr.get_message().content}")
        for msg_id in add_list:
            msg = [x for x in messages if x.id == msg_id][0]
            last_msg_mgr.add_response(msg)
            print(f"response: {msg.content}")

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


# See intro to https://cookbook.openai.com/examples/assistants_api_overview_python to
# explain difference between Completions (used here) and Assistants API.
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
