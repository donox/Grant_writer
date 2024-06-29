import json
import csv
from assistant.message_manager import Message


class ThreadManager(object):
    def __init__(self, file_path):
        self.grant_builder = None
        self.file = file_path
        self.known_oai_threads = []  # These are the threads as recorded in the 'database' (survives over runs)
        with open(self.file, 'r') as thread_data:
            rdr = csv.reader(thread_data)
            for line in rdr:
                if len(line) < 4:
                    break
                usr, thread_name, thread_id, purpose = line
                tmp = {"user": usr,
                       "name": thread_name,
                       "thread_id": thread_id,
                       "purpose": purpose,
                       "ww_thread": None}
                tmp["ww_thread"] = Thread(tmp, self)
                self.known_oai_threads.append(tmp)
        self.message_list = []

    def set_grant_builder(self, grant_builder):  # Needed to avoid circular import with ThreadManager
        self.grant_builder = grant_builder
        for thread in self.known_oai_threads:       # Check in case thread was created before grant_builder defined
            ww_thread = thread["ww_thread"]
            ww_thread.set_grant_builder(self.grant_builder)
            if len(ww_thread.get_id()) > 5:
                self.verify_thread(ww_thread.get_id())

    def verify_thread(self, thread_id):
        client = self.grant_builder.get_client()
        res = client.beta.threads.retrieve(thread_id)
        if res:
            return True
        else:
            raise ValueError(f"Thread {thread_id} does not exist")

    def get_thread_list_user(self, user):
        user_threads = []
        for thread in self.known_oai_threads:
            if thread['user'] == user or thread['user'] == '*':
                user_threads.append(thread)
        return user_threads

    def add_new_thread(self, thread, user, name, purpose):
        thread_id = thread.id
        tmp = {"user": user,
               "name": name,
               "thread_id": thread_id,
               "purpose": purpose,
               "ww_thread": None}
        tmp["ww_thread"] = Thread(tmp, self)
        self.known_oai_threads.append(tmp)
        self.update_thread_file()
        return True

    def update_thread_file(self):
        try:
            with open(self.file, 'w') as thread_data:
                writer = csv.writer(thread_data)
                for row in self.known_oai_threads:
                    row_list = [row[x] for x in row if type(row[x]) is str]
                    writer.writerow(row_list)     # remove reference to thread object
        except Exception as e:
            print(f"Failure writing threads to file: {e.args}")
            raise e

    def create_run(self, oai_thread, user, name):
        thread = oai_thread["ww_thread"]
        return thread

    def get_known_thread_entry_from_name(self, name):
        for thread in self.known_oai_threads:
            if thread["name"] == name:
                return thread["ww_thread"]
        print(f"Thread not found: {name}")
        raise ValueError(f"unknown thread name {name}")

    def get_oai_thread(self, thread_id):
        thread = self.grant_builder.get_oai_thread(thread_id)
        return thread

    def get_grant_builder(self):
        return self.grant_builder

    def delete_thread(self, thread_name):
        self.known_oai_threads = [x for x in self.known_oai_threads if x['name'] != thread_name]
        self.update_thread_file()


class Thread(object):
    def __init__(self, data, thread_manager):
        self.thread_manager = thread_manager
        self.thread_name = data['name']
        self.oai_thread = None
        self.thread_id = data['thread_id']
        self.user = data['user']
        self.purpose = data['purpose']
        self.thread_instantiated = False
        self.message_list = []
        self.grant_builder = self.thread_manager.get_grant_builder()

    def set_grant_builder(self, gb):            # Defending against Threads created before manager knows builder
        self.grant_builder = gb

    def get_oai_thread(self):
        if not self.thread_instantiated:
            self.oai_thread = self.thread_manager.get_oai_thread(self.thread_id)
            self.thread_instantiated = True
        return self.oai_thread

    def get_thread_name(self):
        return self.thread_name

    def get_id(self):
        return self.thread_id

    def update_messages(self):
        self.oai_thread = self.get_oai_thread()
        if self.message_list:
            most_recent_message = self.message_list[0]  # messages in reverse chrono order
            message_id = most_recent_message.get_message_id()
        else:
            message_id = None
        raw_messages = self.grant_builder.get_raw_messages(self.oai_thread, after=message_id)
        processed_messages = []
        for msg in raw_messages:
            new_message = Message(self.grant_builder, self.thread_id)
            new_message.set_message_content(msg)
            processed_messages.append(new_message)
        if processed_messages:
            processed_messages[0].set_last_message()
        self.message_list = processed_messages + self.message_list

    def get_most_recent_responses(self):
        """Return list of messages from beginning of message list to end or message marked as last entry."""
        result = []
        if len(self.message_list) > 1:
            result.append(self.message_list[0])    # first message is marked as the end.
        for message in self.message_list[1:]:
            if message.get_last_message():
                break
            result.append(message)
        return result

    def get_message_from_id(self, message_id):
        for msg in self.message_list:
            if msg.get_message_id() == message_id:
                return msg
        return None

