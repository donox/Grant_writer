import json
import csv


class ThreadManager(object):
    def __init__(self, file_path):
        self.grant_builder = None
        self.file = file_path
        self.known_threads = []     # These are the threads as recorded in the 'database' (survives over runs)
        self.in_use_threads = []    # These are Thread objects created since application startup
        with open(self.file, 'r') as thread_data:
            rdr = csv.reader(thread_data)
            for usr, thread_name, thread_id, purpose in rdr:
                tmp = {"user": usr,
                       "name": thread_name,
                       "thread_id": thread_id,
                       "purpose": purpose}
                self.known_threads.append(tmp)
                thread_object = Thread(tmp, self)
                self.in_use_threads.append(thread_object)

    def set_grant_builder(self, grant_builder):         # Needed to avoid circular call with ThreadManager
        self.grant_builder = grant_builder

    def get_thread_list_user(self, user):
        user_threads = []
        for thread in self.known_threads:
            if thread['user'] == user or thread['user'] == '*':
                user_threads.append(thread)
        return user_threads

    def add_new_thread(self, thread, user, name, purpose):
        thread_id = thread.id
        self.known_threads.append({"user": user,
                                   "name": name,
                                   "thread_id": thread_id,
                                   "purpose": purpose})
        self.update_thread_file()
        return True

    def update_thread_file(self):
        try:
            with open(self.file, 'w') as thread_data:
                writer = csv.writer(thread_data)
                for row in self.known_threads:
                    writer.writerow(row.values())
        except Exception as e:
            print(f"Failure writing threads to file: {e.args}")
            raise e

    def create_run(self, oai_thread, user, name):
        thread = Thread(oai_thread, self.get_known_thread_entry_from_name(name))
        self.in_use_threads.append(thread)
        return thread

    def get_known_thread_entry_from_name(self, name):
        for thread in self.in_use_threads:
            if thread.get_thread_name() == name:
                return thread
        print(f"Thread not found: {name}")
        raise ValueError(f"unknown thread name {name}")

    def get_oai_thread(self, thread_id):
        thread = self.grant_builder.get_oai_thread(thread_id)
        return thread


class Thread(object):
    def __init__(self, data, thread_manager):
        self.thread_manager = thread_manager
        self.thread_name = data['name']
        self.oai_thread = None
        self.thread_id = data['thread_id']
        self.user = data['user']
        self.purpose = data['purpose']
        self.thread_instantiated = False
        self.messages_instantiated = False

    def get_oai_thread(self):
        if not self.thread_instantiated:
            self.oai_thread = self.thread_manager.get_oai_thread(self.thread_id)
            self.thread_instantiated = True
        return self.oai_thread

    def get_thread_name(self):
        return self.thread_name
