from openai import OpenAI

class VectorStoreManager(object):
    def __init__(self, client, name, vs_id=None, show_json=False):
        self.client = client
        self.show_json = show_json
        self.vector_store_id = vs_id
        if vs_id:
            self.vector_store = self.client.beta.vector_stores.retrieve(vs_id)
            self.store_name = self.vector_store.name
        else:
            self.store_name = name
            self.vector_store = client.beta.vector_stores.create(name=name)
            self.vector_store_id = self.vector_store.id

    def add_files_to_store(self, file_list):
        file_streams = [open(path, "rb") for path in file_list]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.vector_store.id, files=file_streams
        )
        return file_batch

    def remove_files_from_store(self, list_of_files):
        pass

    def get_vector_store_object(self):
        return self.vector_store

    def get_vector_store_id(self):
        return self.vector_store_id

def get_known_vector_stores():
    store_list = OpenAI.beta.vector_stores.list()
    return [x.id for x in store_list]