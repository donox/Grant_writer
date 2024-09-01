# app/services.py
class GenericService:
    def __init__(self, data_store):
        self.data_store = data_store

    def get_item(self, list_type, generic_id):
        if list_type in self.data_store.data and generic_id in self.data_store.data[list_type]:
            return self.data_store.data[list_type][generic_id]
        return None

    def update_item(self, list_type, generic_id, update_data):
        if list_type in self.data_store.data and generic_id in self.data_store.data[list_type]:
            self.data_store.data[list_type][generic_id].update(update_data)
            return self.data_store.data[list_type][generic_id]
        return None

    def delete_item(self, list_type, generic_id):
        if list_type in self.data_store.data and generic_id in self.data_store.data[list_type]:
            return self.data_store.data[list_type].pop(generic_id)
        return None