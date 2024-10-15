from flask import current_app
from openai import OpenAI
import json
from db_management.db_manager import DatabaseManager, DBStore
from utilities.run_curl import execute_curl_command


class VectorStoreManager(object):
    def __init__(self, client):
        self.client = client
        self.vector_store_list = []
        self.update_existing_vector_stores()

    def update_existing_vector_stores(self):
        vs_list = self.client.beta.vector_stores.list()
        known_vs_id_list = [x.get_vector_store_id() for x in self.vector_store_list]
        for vs in vs_list:
            if vs.id not in known_vs_id_list:
                mgr = VectorStore(self.client, vs.name, vs_id=vs.id)
                self.vector_store_list.append(mgr)

    def get_vector_store_by_id(self, store_id):
        result = None
        for vs in self.vector_store_list:
            if vs.get_vector_store_id() == store_id:
                result = {'model': vs}    # generics is expecting a dict
                break
        return result

    def get_object_by_id(self, object_id):
        return self.get_vector_store_by_id(object_id)

    def get_vector_store_by_name(self, store_name):
        result = None
        for vs in self.vector_store_list():
            if vs.get_vector_store_name() == store_name:
                result = vs
                break
        return result

    def get_vector_stores(self):
        return self.vector_store_list

    def get_vector_stores_list(self):
        return self.get_vector_stores()

    def get_objects_list(self):  # Support for generic list
        return self.get_vector_stores_list()

    def get_vector_stores_as_list_of_dictionaries(self):
        result = []
        for vector_store in self.get_vector_stores():
            result.append({"name": vector_store.get_vector_store_name(),
                           "id": vector_store.get_vector_store_id()})
        return result

    def add_new_vector_store(self, name):
        new_vs = VectorStore(self.client, name)
        self.vector_store_list.append(new_vs)
        return new_vs

    def delete_store(self, store_id):
        this_store = None
        for x in self.vector_store_list:
            if x.get_vector_store_id() == store_id:
                this_store = x
        if not this_store:
            print(f"store {store_id} was not found getting error")
            return False
        try:
            result = self.client.beta.vector_stores.delete(this_store.get_vector_store_id())
        except Exception as e:  # openAI - NotFoundError
            print(f"store {store_id} was not found getting error {e.args}")
            return False
        if result.deleted:
            self.vector_store_list.remove(this_store)
            this_store = None
        return result.deleted  # True/False


class VectorStore(object):
    def __init__(self, client, name, vs_id=None):
        # TODO:  Need to add description, but it must be kept outside OAI, so need db of some sort.
        self.client = client
        self.vector_store_id = vs_id
        if vs_id:
            self.oai_vector_store = self.client.beta.vector_stores.retrieve(vs_id)
            self.store_name = self.oai_vector_store.name
        else:
            self.store_name = name
            self.oai_vector_store = client.beta.vector_stores.create(name=name)
            self.vector_store_id = self.oai_vector_store.id

    def add_files_to_store(self, file_list):
        file_streams = [open(path, "rb") for path in file_list]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=self.oai_vector_store.id, files=file_streams
        )
        return file_batch

    def get_list_of_files_in_store(self):
        vector_store_files = self.client.beta.vector_stores.files.list(
            vector_store_id=self.oai_vector_store.id
        )
        filenames = []
        for v_file in vector_store_files:
            fn_id = v_file.id
            file = self.client.files.retrieve(fn_id)
            filename = file.filename
            filenames.append({'text': filename, 'id': fn_id, 'children': []})
        return filenames

    def delete_files_from_vector_store(self, list_of_file_ids):
        try:
            for file_id in list_of_file_ids:
                deleted_vector_store_file = self.client.beta.vector_stores.files.delete(
                    vector_store_id=self.vector_store_id,
                    file_id=file_id
                )
                file_name = deleted_vector_store_file.filename
                self.client.files.delete(file_name)
                print(f"Deleted file {file_id} from vector store {self.vector_store_id}: {file_name}")
            return True
        except Exception as e:
            print(f"Error deleting files from vector store {self.vector_store_id}: {e}")
            return False

    def get_vector_store_object(self):
        return self.oai_vector_store

    def get_vector_store_id(self):
        return self.vector_store_id

    def delete_store(self, store_id):
        pass

    def get_vector_store_name(self):
        return self.store_name

    # def get_content_data(self):
    #     res = {"name": self.store_name,
    #            "id": self.vector_store_id,
    #            }
    #     return res
    #
    # def get_content_data(self):
    #     res = json.loads(self.oai_vector_store.to_json())
    #     return res

    def to_json(self):
        res = json.loads(self.oai_vector_store.to_json())
        res['name'] = self.store_name
        v_files = self.get_list_of_files_in_store()
        res['files'] = v_files
        res['model'] = self
        return res


def get_known_vector_store_ids():
    store_list = OpenAI.beta.vector_stores.list()
    return [x.id for x in store_list]
