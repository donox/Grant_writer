# app/controller.py
class GenericController:
    def __init__(self, generic_service):
        self.generic_service = generic_service

    def handle_request(self, function, list_type, generic_id, data=None):
        if function == 'get':
            return self.generic_service.get_item(list_type, generic_id)
        elif function == 'update':
            return self.generic_service.update_item(list_type, generic_id, data)
        elif function == 'delete':
            return self.generic_service.delete_item(list_type, generic_id)
        else:
            return {'error': 'Invalid operation'}