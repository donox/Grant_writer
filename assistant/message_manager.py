from openai import OpenAI


class MessageManager(object):
    def __init__(self, client, thread):
        self.client = client
        self.thread = thread
        self.message = None
        self.content = None
        self.role = None
        self.attachments = []
        self.files = []

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
            return self.message
        except Exception as e:
            print(e)

    def get_message(self):
        return self.message

