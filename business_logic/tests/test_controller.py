# tests/test_controller.py
import pytest
from business_logic.app.models import DataStore
from business_logic.app.services import GenericService
from business_logic.app.controller import GenericController


@pytest.fixture
def generic_controller():
    data_store = DataStore()
    generic_service = GenericService(data_store)
    return GenericController(generic_service)


def test_get_item(generic_controller):
    result = generic_controller.handle_request('get', 'assistant', '1')
    assert result['name'] == 'Assistant 1'


def test_update_item(generic_controller):
    update_data = {'name': 'Updated User 1'}
    result = generic_controller.handle_request('update', 'user', '1', update_data)
    assert result['name'] == 'Updated User 1'


def test_delete_item(generic_controller):
    result = generic_controller.handle_request('delete', 'assistant', '2')
    assert result['name'] == 'Assistant 2'
    assert generic_controller.handle_request('get', 'assistant', '2') is None


def test_invalid_operation(generic_controller):
    result = generic_controller.handle_request('invalid', 'assistant', '1')
    assert result == {'error': 'Invalid operation'}