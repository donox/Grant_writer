from openai import OpenAI


class MessageManager(object):
    def __init__(self, client, thread):
        self.client = client
        self.thread = thread
        self.message = None     # message and message_id and content refer to the user/system query message
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
        file_object = self.client.files.create(file=open(path, "rb"), purpose="assistants")
        self.files.append(file_object)
        self.attachments.append({"file_id": file_object.id,
                                 "tools": [{"type": "file_search"}]})

    def create_message(self):
        if not self.content or not self.role:
            raise AssertionError("No content or role for message")
        try:
            self.message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=self.role,
                content=self.content,
                attachments=self.attachments,
            )
            self.message_id = self.message.id
            return self.message
        except Exception as e:
            print(e)

    def create_response_text(self):
        response = ""       # this is getting null !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        for tmp in self.responses:
            for content in tmp.content:
                content_text = content.text.value
                response += content_text + "\n\n"
        return response

    def add_response(self, msg):
        self.responses.append(msg)

    def get_message(self):
        return self.message

    def get_responses(self):
        return self.responses

    def get_response_ids(self):
        return [x.id for x in self.responses]

    def get_message_id(self):
        return self.message_id

    def get_thread_id(self):
        return self.message.thread_id

