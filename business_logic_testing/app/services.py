# app/services.py
from ui_client.routes.generics import get_model_class, get_model_manager, get_object_from_id, get_id_from_name


class GenericService:
    def __init__(self, data_store, global_context):
        self.data_store = data_store    # currently unused
        self.ci = global_context["ci"]
        self.cmd_handler = global_context["cmds"]
        self.config = global_context["config"]

    def get_model_manager(self, list_type):
        model_manager = get_model_manager(list_type)
        return model_manager

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
