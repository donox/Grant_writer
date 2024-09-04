from app.models import DataStore
from app.services import GenericService
from app.controller import GenericController
from ui_control.client_interface import ClientInterface
from ui_control.command_processor import Commands
from config import Config
import configparser


def main():
    cmd_path = '/home/don/PycharmProjects/grant_assistant/Temp/commands.json'
    outfile = "/home/don/Documents/Temp/outfile.txt"

    config = configparser.ConfigParser()
    with open("/home/don/PycharmProjects/grant_assistant/config_file.cfg") as source:
        config.read(source.name)
    handler = Commands(cmd_path, config, outfile)
    client_ui = ClientInterface(handler)

    data_store = DataStore()
    generic_service = GenericService(data_store)
    controller = GenericController(generic_service)

    # # Simulate some requests
    # print(controller.handle_request('get', 'assistant', '1'))
    # print(controller.handle_request('update', 'user', '2', {'name': 'Updated User 2'}))
    # print(controller.handle_request('delete', 'assistant', '2'))


if __name__ == '__main__':
    main()
