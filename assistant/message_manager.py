

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
        try:
            self.message = self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role=self.role,
                content=self.content,
                attachments=self.attachments,
            )
        except Exception as e:
            print(e)

    def get_message(self):
        return self.message




        # self.test_file = self.client.files.create(file=open("/home/don/Documents/Wonders/test forms/Kronkosky - LOI.docx", "rb"),
        #                                 purpose="assistants")
        # self.message = self.client.beta.threads.messages.create(
        #     thread_id=self.thread.id,
        #     role="user",
        #     content="Fill out the LOI in the associated file using information from the vector store",
        #     attachments=[{"file_id": self.test_file.id,
        #                   "tools": [{"type": "file_search"}]}]
