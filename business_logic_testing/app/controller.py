# app/controller.py
import sys


class GenericController:
    def __init__(self, generic_service, global_context):
        self.generic_service = generic_service
        self.ci = global_context["ci"]
        self.cmd_handler = global_context["cmds"]
        self.config = global_context["config"]

    def handle_request(self, function, list_type, generic_id=None, data=None):
        if function == 'get_model_manager':
            return self.generic_service.get_model_manager(list_type)
        elif function == 'get_details':
            return self.generic_service.get_item(list_type, generic_id)
        elif function == 'update':
            return self.generic_service.update_item(list_type, generic_id, data)
        elif function == 'delete':
            return self.generic_service.delete_item(list_type, generic_id)
        else:
            return {'error': 'Invalid operation'}


class ThreadController:
    def __init__(self, thread_service, global_context):
        self.thread_service = thread_service
        self.ci = global_context["ci"]
        self.cmd_handler = global_context["cmds"]
        self.config = global_context["config"]

    def handle_request(self, function, thread_name=None):
        if function == 'get_conversation_json':
            thread = self.thread_service.get_known_thread_entry_from_name(thread_name)
            result = self.thread_service.get_conversation_json(thread.get_id())
            return result
        else:
            return {'error': 'Invalid operation'}