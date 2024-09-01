from app.models import DataStore
from app.services import GenericService
from app.controller import GenericController

def main():
    data_store = DataStore()
    generic_service = GenericService(data_store)
    controller = GenericController(generic_service)

    # Simulate some requests
    print(controller.handle_request('get', 'assistant', '1'))
    print(controller.handle_request('update', 'user', '2', {'name': 'Updated User 2'}))
    print(controller.handle_request('delete', 'assistant', '2'))

if __name__ == '__main__':
    main()