

class Message(object):
    def __init__(self, grant_builder, thread):
        self.grant_builder = grant_builder
        self.thread = thread    # thread is the thread controller (user level), not oaithread
        self.oai_message = None
        self.message_id = None
        self.content = None
        self.role = None
        self.attachments = []
        self.files = []
        self.responses = []                 # WHY IS THIS NEEDED - never created
        self.end_query_message = False      # Set to true on the most recent (last) message on any query (run)

    def add_content_and_create_message_in_thread(self, content, role):
        # Need to add any file attachments before calling this method
        self.content = content
        self.role = role
        oai_message = self.grant_builder.add_message_to_thread(self.thread, content, role)
        self.message_id = oai_message.id

    def set_last_message(self):
        self.end_query_message = True

    def get_last_message(self):
        return self.end_query_message

    def add_file_attachment(self, path):
        file_object = self.grant_builder.get_file_object(path)
        self.files.append(file_object)
        self.attachments.append({"file_id": file_object.id,
                                 "tools": [{"type": "file_search"}]})

    def create_response_text(self):
        return self.content
        # response = ""       # this is getting null !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # for tmp in self.responses:
        #     for content in tmp.content:
        #         content_text = content.text.value
        #         response += content_text + "\n\n"
        return response

    def add_response(self, msg):          # THIS IS NEVER CALLED - What is the idea of multiple responses for a message
        self.responses.append(msg)

    def get_oai_message(self):
        return self.message

    def get_responses(self):
        return self.responses

    def get_response_ids(self):
        return [x.id for x in self.responses]

    def get_message_id(self):
        return self.message_id

    def get_thread_id(self):
        return self.message.thread_id

    def create_oai_message(self):
        foo = 3
        result = self.grant_builder.create_oai_message(self.role, self.content, self.thread, self.attachments)
        return result

    def update_message(self, message_id, role, thread_id, content):
        oai_client = self.grant_builder.get_client()
        oai_client.beta.Assistant.update_message

    def set_message_content(self, raw_content):
        self.oai_message = raw_content
        self.message_id = raw_content['id']
        self.role = raw_content['role']
        self.content = raw_content['content'][0]['text']['value']

    def get_role(self):
        return self.role

    def get_content(self):
        return self.content

    def get_content_dict(self):             # Note Message does not know thread used to create it
        result = {'role': self.role,
                  'content': self.content,
                  'message_id': self.message_id}
        return result


