import json
import csv
from assistant.message_manager import Message


class ThreadManager(object):
    def __init__(self, file_path):
        self.grant_builder = None
        self.client = None
        self.file = file_path
        self.known_oai_threads = []  # These are the threads as recorded in the 'database' (survives over runs)
        with open(self.file, 'r') as thread_data:
            rdr = csv.reader(thread_data)
            for line in rdr:
                if len(line) < 4:
                    break
                usr, thread_name, thread_id, purpose = line  # todo remove use of 'user'
                tmp = {"user": usr,
                       "name": thread_name,
                       "id": thread_id,
                       "purpose": purpose,
                       "ww_thread": None}
                tmp["ww_thread"] = Thread(tmp, self)
                self.known_oai_threads.append(tmp)

    def set_grant_builder(self, grant_builder):  # Needed to avoid circular import with ThreadManager
        self.grant_builder = grant_builder
        self.client = grant_builder.get_client()
        for thread in self.known_oai_threads:  # Check in case thread was created before grant_builder defined
            ww_thread = thread["ww_thread"]
            ww_thread.set_grant_builder(self.grant_builder)
            if len(ww_thread.get_id()) > 5:
                self.verify_thread(ww_thread.get_id())   # TODO: should trap error return

    def verify_thread(self, thread_id):
        client = self.grant_builder.get_client()
        res = client.beta.threads.retrieve(thread_id)
        if res:
            return True
        else:
            raise ValueError(f"Thread {thread_id} does not exist")

    def get_thread_list(self):
        return self.known_oai_threads

    def get_objects_list(self):  # Support for generic list
        return self.get_thread_list()

    def add_new_thread(self, data):
        thread = self.client.beta.threads.create()
        thread_id = thread.id
        tmp = {"name": data['name'],
               "id": thread_id,
               "purpose": data['purpose'],
               "user": data['user'],
               "ww_thread": None}
        tmp["ww_thread"] = Thread(tmp, self)
        self.known_oai_threads.append(tmp)
        self.update_thread_file()
        return True

    def update_thread_file(self):
        try:
            with open(self.file, 'w') as thread_data:
                writer = csv.writer(thread_data)
                rows_written = []  # Hack to try to stop proliferation of copies
                for row in self.known_oai_threads:
                    # row:  don,t38,thread_lG0UyYgzw0DmHNffTOOwJPy1,hjgk
                    row_list = [row[x] for x in row if type(row[x]) is str]
                    if row_list[1] not in rows_written:
                        rows_written.append(row_list[1])
                        writer.writerow(row_list)  # remove reference to thread object
                thread_data.close()
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

    def delete_thread(self, thread_id):
        self.known_oai_threads = [x for x in self.known_oai_threads if x['id'] != thread_id]
        self.update_thread_file()


class Thread(object):
    def __init__(self, data, thread_manager):
        self.thread_manager = thread_manager
        self.thread_name = data['name']
        self.oai_thread = None
        self.thread_instantiated = False  # means has oai_thread set
        self.thread_id = data['id']
        self.user = data['user']
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
        result_id = 'rslt' + tail_list[0].get_message_id()
        res = {
            "id": result_id,
            "text": tail_list[0].get_content()[0:30],
            "state": {
                "opened": True,
                "selected": False
            },
            "datums": {
                "role": tail_list[0].get_role(),
                "content": tail_list[0].get_content(),
            },
            "children": result,
        }
        return res

    def build_query_list(self):
        """Create/update query list  of id's of messages with role=user."""
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
