import json
import time
from typing import List, Any
from openai import OpenAI
from assistant.message_manager import Message
from assistant.thread_manager import Thread
from assistant.assistant_manager import Assistant, AssistantManager

#  URL's  used to try to get this to work!!
#  https://github.com/openai/openai-python/blob/main/src/openai/resources/beta/threads/threads.py
#  https://platform.openai.com/docs/assistants/tools/file-search
#  https://platform.openai.com/assistants


class GrantWriter(object):
    def __init__(self, api_key, output_mgr, thread_manager):
        self.client = OpenAI(api_key=api_key)
        self.assistant_list = []
        self.output_mgr = output_mgr
        self.thread_manager = thread_manager
        self.assistant_manager = None
        # OpenAI.beta.threads.runs.list()

    def set_assistant_manager(self, assistant_manager):    # Avoid circular calls
        self.assistant_manager = assistant_manager

    def add_message_to_thread(self, thread, content, role):
        """add new message to existing thread, returning OIA message."""
        thread_id = thread.get_id()
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content)
        return message

    def update_message(self, message_id, role, thread_name, content):
        foo = 3
        thread = self.thread_manager.get_known_thread_entry_from_name(thread_name)
        msg = thread.get_message_from_id(message_id)
        if msg:
            msg.update_message(message_id, role, thread.get_id(), content)
            return True
        return False


    def get_client(self):
        return self.client      # client is an OpenAI object, not an assistant

    # def retrieve_existing_assistants(self):
    #     self.assistant_manager.retrieve_existing_assistants()

    # def get_thread_list_user(self, user):
    #     result = self.thread_manager.get_thread_list_user(user)
    #     return result

    def get_thread_by_name(self, thread_name):
        thread = self.thread_manager.get_known_thread_entry_from_name(thread_name)
        return thread

    def add_new_thread(self, data):
        thread = self.client.beta.threads.create()
        result = self.thread_manager.add_new_thread(thread, data['user'], data['name'], data['purpose'])
        return result

    def add_new_assistant(self, data):
        result = Assistant(self.client, data['name'])
        return result

    def delete_thread(self, thread_id):
        try:
            result = self.client.beta.threads.delete(thread_id)
        except Exception as e:     # openAI - NotFoundError
            print(f"Thread {thread_name} was not found getting error {e.args}")
            return False
        if result.deleted:
            self.thread_manager.delete_thread(thread_id)
        return result.deleted               # True/False

    # def get_assistant_list(self):
    #     result = []
    #     for assistant in self.assistant_list:
    #         result.append({'name': assistant.get_name(),
    #                        'id': assistant.get_id()})
    #     return result

    def create_run(self, user, name, assistant_id):
        thread = self.thread_manager.get_known_thread_entry_from_name(name)
        thread_id = thread.thread_id
        oai_thread = self.get_oai_thread(thread_id)
        assistant = self.assistant_manager.get_assistant_from_id(assistant_id)
        if assistant:
            run = self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant.get_id())
            run = self.wait_on_run(run, oai_thread)
            return run
        else:
            print(f"Assistant: {assistant_id} not in existing assistants.")
            return False

    def wait_on_run(self, run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    def get_oai_thread(self, thread_id):
        thread = self.client.beta.threads.retrieve(thread_id)
        return thread

    def get_raw_messages(self, oai_thread, after=None):
        foo = 3
        message_id = after
        if message_id:
            result_str = self.client.beta.threads.messages.list(thread_id=oai_thread.id, order="asc", after=message_id)
        else:
            result_str = self.client.beta.threads.messages.list(thread_id=oai_thread.id, order="asc")
        raw_result = json.loads(result_str.to_json())
        result = []
        for msg in raw_result['data']:
            if msg['role'] and msg['content']:
                result.append(msg)
            else:
                self.client.beta.threads.messages.delete(msg.id, oai_thread.id)
        return result

    def create_oai_message(self, role, content, thread, attachments):
        if not content or not role:
            raise AssertionError("No content or role for message")
        try:
            oai_message = self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role=role,
                content=content,
                attachments=attachments,
            )
            return oai_message
        except Exception as e:
            print(e)

    def get_file_object(self, path):
        file_object = self.client.files.create(file=open(path, "rb"), purpose="assistants")   # Purpose right????
        return file_object




