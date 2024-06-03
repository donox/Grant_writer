

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
        self.responses = []

    def add_content(self, content, role):
        self.content = content
        self.role = role

    def add_file_attachment(self, path):
        file_object = self.grant_builder.get_file_object(path)
        self.files.append(file_object)
        self.attachments.append({"file_id": file_object.id,
                                 "tools": [{"type": "file_search"}]})

    def create_response_text(self):
        response = ""       # this is getting null !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for tmp in self.responses:
            for content in tmp.content:
                content_text = content.text.value
                response += content_text + "\n\n"
        return response

    def add_response(self, msg):
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
        result = self.grant_builder.create_oai_message(self.role, self.content, self.thread, self.attachments)
        foo=3
        return result

    def set_message_content(self, raw_content):
        self.message_id = raw_content['id']
        self.role = raw_content['role']
        self.oai_message = raw_content
        self.content = raw_content['content'][0]['value']


