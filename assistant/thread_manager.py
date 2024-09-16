import json
import csv
import sqlite3
from assistant.message_class import Message
from db_management.db_manager import DBThread
from db_management.db_utils import get_db_manager


class ThreadManager(object):
    def __init__(self, db_path):
        self.grant_builder = None
        self.client = None
        self.db_path = db_path
        # oai_thread is dict with 'name', 'owner', 'id' (actual oai id), 'purpose',
        #                         'ww_thread' (pointer to thread object)
        self.known_oai_threads = []
        self.initialize_database()
        self.load_threads_from_database()

    def initialize_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threads (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    purpose TEXT
                )
            ''')
            conn.commit()

    def load_threads_from_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM threads")
            rows = cursor.fetchall()
            for row in rows:
                thread_id, name, owner, purpose = row
                tmp = {
                    "owner": owner,
                    "name": name,
                    "id": thread_id,
                    "purpose": purpose,
                    "ww_thread": None
                }
                tmp["ww_thread"] = Thread(tmp, self)
                self.known_oai_threads.append(tmp)

    def update_thread_file(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for thread in self.known_oai_threads:
                cursor.execute('''
                    INSERT OR REPLACE INTO threads (id, name, owner, purpose)
                    VALUES (?, ?, ?, ?)
                ''', (thread['id'], thread['name'], thread['owner'], thread['purpose']))
            conn.commit()

    def new_update_thread_file(self):
        try:
            threads = DBThread.get_all(self.db_manager)
            current_known_threads = [th['id'] for th in self.known_oai_threads]
            for thread in threads:
                if thread['oai_id'] not in current_known_threads:
                    DBThread.delete(thread['id'])
            db_threads = [th['id'] for th in threads]
            for thread in self.new_known_oai_threads:
                if thread not in db_threads:
                    thread_json = thread.to_json()
                    fields = {
                        "name": thread_json['name'],
                        "id": thread_json['id'],
                        "purpose": thread_json['purpose'],
                        "owner": thread_json['owner'],
                        "extra_data": None
                    }
                    DBThread.create(fields)
        except Exception as e:
            print(f"Failure writing threads to file: {e.args}")
            raise e

    def set_grant_builder(self, grant_builder):  # Needed to avoid circular import with ThreadManager
        self.grant_builder = grant_builder
        self.client = grant_builder.get_client()
        for thread in self.known_oai_threads:  # Check in case thread was created before grant_builder defined
            ww_thread = thread["ww_thread"]
            ww_thread.set_grant_builder(self.grant_builder)
            thread_id = ww_thread.get_id()
            if len(thread_id) > 5:  # id will be long string
                try:
                    res = self.verify_thread(thread_id)
                    if not res:
                        print(f"Warning: Failed to verify thread {thread_id}, Removing from list")
                        self.delete_thread(thread_id)
                except Exception as e:
                    print(f"Warning: Failed to verify thread {thread_id}: {str(e)}")

    def complete_thread_creation(self):
        """Instantiate known_oai_threads.

        This is necessary to allow setup of client before a Thread is able to instantiate
        the oai_threads.  The sequence of events is driven as a part of the setup command
        in the command processor. """
        if not self.client:
            raise ValueError("Client has not been created.  Out of sequence setup.")
        for thread in self.known_oai_threads:
            x = thread['ww_thread'].get_oai_thread()
            if not x:
                raise ValueError(f"unable to instantiate oai_thread: {thread.get_id()}")

    def verify_thread(self, thread_id):
        try:
            res = self.client.beta.threads.retrieve(thread_id)
            return True
        except Exception as e:
            print(f"Thread {thread_id} does not exist or couldn't be retrieved: {str(e)}")
            return False

    def get_thread_list(self):
        return self.known_oai_threads

    def get_objects_list(self):  # Support for generic list
        return self.get_thread_list()

    def add_new_thread(self, data):
        thread = self.client.beta.threads.create()
        thread_id = thread.id
        tmp = {
            "name": data['name'],
            "id": thread_id,
            "purpose": data['purpose'],
            "owner": data['owner'],
            "ww_thread": None
        }
        tmp["ww_thread"] = Thread(tmp, self)
        self.known_oai_threads.append(tmp)
        self.update_thread_file()
        return True

    def add_preexisting_thread(self, thread_data):
        """
        Add a preexisting thread to the database and known_oai_threads list.

        :param thread_data: A dictionary containing thread information:
                            {'id': str, 'name': str, 'user': str, 'purpose': str}
        :return: True if the thread was added successfully, False otherwise
        """
        required_keys = ['id', 'name', 'owner', 'purpose']
        if not all(key in thread_data for key in required_keys):
            print("Error: Missing required thread data")
            return False

        # Check if the thread already exists
        existing_thread = next((t for t in self.known_oai_threads if t['id'] == thread_data['id']), None)
        if existing_thread:
            print(f"Thread with ID {thread_data['id']} already exists")
            return False

        # Add to known_oai_threads
        tmp = {
            "owner": thread_data['owner'],
            "name": thread_data['name'],
            "id": thread_data['id'],
            "purpose": thread_data['purpose'],
            "ww_thread": None
        }
        tmp["ww_thread"] = Thread(tmp, self)
        self.known_oai_threads.append(tmp)

        # Add to database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO threads (id, name, owner, purpose)
                VALUES (?, ?, ?, ?)
            ''', (thread_data['id'], thread_data['name'], thread_data['owner'], thread_data['purpose']))
            conn.commit()

        print(f"Thread {thread_data['name']} (ID: {thread_data['id']}) added successfully")
        return True

    def delete_thread(self, thread_id):
        self.known_oai_threads = [x for x in self.known_oai_threads if x['id'] != thread_id]
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
            conn.commit()

    # def update_thread_file(self):
    #     try:
    #         with open(self.file, 'w') as thread_data:
    #             writer = csv.writer(thread_data)
    #             rows_written = []
    #             for row in self.known_oai_threads:
    #                 thread_id = row["id"]
    #                 if thread_id not in rows_written:
    #                     rows_written.append(thread_id)
    #                     row_to_write = [row['owner'], row['name'], row['id'], row['purpose']]
    #                     writer.writerow(row_to_write)
    #             thread_data.close()
    #     except Exception as e:
    #         print(f"Failure writing threads to file: {e.args}")
    #         raise e

    def create_run(self, oai_thread, owner, name):
        thread = oai_thread["ww_thread"]
        return thread

    def get_known_thread_entry_from_name(self, name):
        for thread in self.known_oai_threads:
            if thread["name"] == name:
                return thread["ww_thread"]
        print(f"Thread not found: {name}")
        raise ValueError(f"unknown thread name {name}")

    def get_known_thread_by_id(self, thread_id):
        """Get thread entry from (non-oai) id."""
        for thread in self.known_oai_threads:
            if thread['ww_thread'].get_id() == thread_id:
                return thread
        print(f"Thread not found: {thread_id}")
        raise ValueError(f"unknown thread name {thread_id}")

    def get_known_thread_by_oai_id(self, oai_thread_id):
        for thread in self.known_oai_threads:
            if thread['id'] == oai_thread_id:
                return thread["ww_thread"]
        print(f"Thread not found: {oai_thread_id}")
        raise ValueError(f"unknown thread name {oai_thread_id}")

    def get_object_by_id(self, object_id):
        """Get thread using generic call."""
        thread = self.get_known_thread_by_id(object_id)
        # oai_thread = thread.get_oai_thread()
        return thread

    def get_object_from_name(self, object_name):
        """Get thread using generic call."""
        return self.get_known_thread_entry_from_name(object_name)

    def get_oai_thread(self, thread_id):
        thread = self.grant_builder.get_oai_thread(thread_id)
        return thread

    def get_grant_builder(self):
        return self.grant_builder



class Thread(object):
    def __init__(self, data, thread_manager):
        self.thread_manager = thread_manager
        self.thread_name = data['name']
        self.oai_thread = None
        self.thread_instantiated = False  # means has oai_thread set
        self.thread_id = data['id']
        self.owner = data['owner']
        self.purpose = data['purpose']
        self.message_list = []
        self.query_list = []
        self.grant_builder = self.thread_manager.get_grant_builder()

    def make_thread_jstree_json(self):
        self.build_query_list()
        jstree = []
        for message_id in self.query_list:
            qr = self.make_query_response_json(message_id)
            jstree.append(qr)
        return jstree

    def make_query_response_json(self, msg_id=None):
        """Create json for specified query/response.

        A query response consists of messages beginning with the specified id and
        continuing to the end of the message list or the next message with an id
        in the query_list. If no message id is given, the last message in
        the query list is presumed."""
        following_query = None  # id of query following msg_id if not at end
        if msg_id:
            last_query = msg_id
            if last_query == self.query_list[-1]:
                is_most_recent = True
            else:
                found_it = False
                for nbr, this_id in enumerate(self.query_list):
                    if this_id == last_query:
                        is_most_recent = False
                        following_query = self.query_list[nbr + 1]
                        found_it = True
                        break
                else:
                    raise ValueError(f"Did not find message: {msg_id} in self.query_list.")
        else:
            msg_id = self.query_list[-1]
            is_most_recent = True

        for nbr, this_msg in enumerate(self.message_list):
            this_msg_id = this_msg.get_message_id()
            if this_msg_id == msg_id:
                tail_list = self.message_list[nbr:]
                break
        if not is_most_recent:  # implies following_query is not None
            for nbr, this_msg in enumerate(tail_list):
                this_msg_id = this_msg.get_message_id()
                if following_query == this_msg_id:
                    tail_list = tail_list[:nbr]
                    break
            else:
                raise ValueError(f"Failed to find 'following_query' to build tail_list")

        # the first element of tail_list is the query, all following are the responses.
        result = []
        for msg in tail_list[1:]:  # just get responses
            result.append(msg.make_message_json())
        tl_0 = tail_list[0]
        tl_content = str.strip(tl_0.get_content())
        result_id = 'rslt' + tl_0.get_message_id()
        res = {
            "id": result_id,
            "text": tl_content,
            "state": {
                "opened": False,
                "selected": False
            },
            "datums": {
                "role": tl_0.get_role(),
                "content": tl_content,
                "datetime": tl_0.get_time(),
            },
            "children": result,
        }
        return res

    def build_query_list(self):
        """Create/update query list of id's of messages with role=owner."""
        self.query_list = []
        for msg in self.message_list:
            if msg.get_role() == 'user':
                self.query_list.append(msg.get_message_id())

    def set_grant_builder(self, gb):  # Defending against Threads created before manager knows builder
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
            result.append(self.message_list[0])  # first message is marked as the end.
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

    def get_content_data(self):
        res = json.loads(self.oai_thread.to_json())
        return res

    def to_json(self):
        """Make JSON object with fields from OAI object and additional fields unique to object type."""
        res = self.get_content_data()
        res['name'] = self.thread_name
        res['description'] = self.purpose
        print(f"THREAD TO JSON: {res}")
        return res
