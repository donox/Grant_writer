# tests/test_controller.py
import pytest
import configparser
import pytest
from unittest.mock import Mock, patch

from ui_control.client_interface import ClientInterface
from ui_control.command_processor import Commands
from assistant.assistant_manager import Assistant, AssistantManager
from assistant.thread_manager import Thread, ThreadManager
from assistant.vector_store_manager import VectorStore, VectorStoreManager
from business_logic_testing.app.models import DataStore
from business_logic_testing.app.services import GenericService
from business_logic_testing.app.controller import GenericController


class MockFlaskApp:
    def __init__(self, initial_config=None):
        self.config = initial_config or {}

    def set_config(self, key, value):
        self.config[key] = value

    def get_config(self, key, default=None):
        return self.config.get(key, default)


@pytest.fixture(scope="session")
def mock_flask_app():
    return MockFlaskApp({
        'DEBUG': True,
        'TESTING': True,
    })


@pytest.fixture(scope="session")
def patched_current_app(mock_flask_app):
    with patch('ui_control.command_processor.current_app', mock_flask_app), \
         patch('ui_client.routes.generics.current_app', mock_flask_app):
        yield mock_flask_app

@pytest.fixture(scope="session")
def global_context(patched_current_app):
    print("Setting up global context (session scope)")
    cmd_path = '/home/don/PycharmProjects/grant_assistant/Temp/commands.json'
    outfile = "/home/don/Documents/Temp/outfile.txt"

    config = configparser.ConfigParser()
    with open("/home/don/PycharmProjects/grant_assistant/config_file.cfg") as source:
        config.read(source.name)
    handler = Commands(cmd_path, config, outfile)
    handler.cmd_setup({})
    client_ui = ClientInterface(handler)

    patched_current_app.set_config('SECRET_KEY', config['keys']['flaskKey'])
    patched_current_app.set_config('RUN_SETUP', False)
    patched_current_app.set_config('CLIENT_INTERFACE', client_ui)
    patched_current_app.set_config('ASSISTANT', config['keys']['assistant'])
    patched_current_app.set_config('ASSISTANT_MANAGER', handler.assistant_manager)
    patched_current_app.set_config('THREAD_MANAGER', handler.thread_manager)
    patched_current_app.set_config('STORE_MANAGER', handler.vector_store_manager)

    app_config = {"ci": client_ui,
                  "cmds": handler,
                  "config": config,
                  }
    yield app_config
    print("Tearing down global data (session scope)")


@pytest.fixture
def generic_controller(global_context):
    data_store = DataStore()
    generic_service = GenericService(data_store, global_context)
    return GenericController(generic_service, global_context)


def test_get_model_manager(generic_controller, patched_current_app):
    result = generic_controller.handle_request('get_model_manager', 'assistant', '1')
    assert type(result) == AssistantManager

# def test_update_item(generic_controller):
#     update_data = {'name': 'Updated User 1'}
#     result = generic_controller.handle_request('update', 'user', '1', update_data)
#     assert result['name'] == 'Updated User 1'
#
#
# def test_delete_item(generic_controller):
#     result = generic_controller.handle_request('delete', 'assistant', '2')
#     assert result['name'] == 'Assistant 2'
#     assert generic_controller.handle_request('get', 'assistant', '2') is None
#
#
# def test_invalid_operation(generic_controller):
#     result = generic_controller.handle_request('invalid', 'assistant', '1')
#     assert result == {'error': 'Invalid operation'}
