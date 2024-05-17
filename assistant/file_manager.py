

class FileManager():
    def __init__(self, client):
        self.client = client
        self.filename = None
        self.file_object = None
        self.file_id = None
        self.openAI_file = None
        self.thread = None

    def attach_file(self, path, purpose):
        self.file_object = open(path, 'rb')
        self.openAI_file = self.client.files.create(file=self.file_object, purpose=purpose)
        self.file_id = self.openAI_file .id
        self.filename = self.openAI_file .filename

    def pass_file_to_thread(self, thread_id):
        self.thread = self.client.beta.threads.retrieve(thread_id)
        self.client.beta.threads.update(thread_id,
                                        tool_resources={"code_interpreter": {"file_ids": [self.openAI_file.id]}})



