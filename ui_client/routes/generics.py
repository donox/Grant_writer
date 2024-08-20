from flask import jsonify, abort, Blueprint
from assistant.assistant_manager import AssistantManager,  Assistant
from assistant.thread_manager import ThreadManager, Thread
from assistant.vector_store_manager import VectorStoreManager, VectorStore

gen = Blueprint("generic", __name__)


def get_model_class(list_type):
    model_mapping = {
        'assistants': Assistant,
        'threads': Thread,
        'stores': VectorStore
    }
    return model_mapping.get(list_type)


def get_model_manager_class(list_type):
    model_mapping = {
        'assistants': AssistantManager,
        'threads': ThreadManager,
        'stores': VectorStoreManager
    }
    return model_mapping.get(list_type)


@gen.route('/get-<list_type>-list/', methods=['GET'])
def get_list(list_type):
    valid_list_types = ['assistants', 'threads', 'stores']
    if list_type not in valid_list_types:
        abort(400, description=f"Invalid list type: {list_type}")

    model_class = get_model_class(list_type)
    model_manager_class = get_model_manager_class(list_type)
    if not model_class:
        abort(500, description=f"Model not found for list type: {list_type}")

    try:
        items = model_manager_class.get_objects_list()
        return jsonify([{'id': item.id, 'name': item.name} for item in items])
    except Exception as e:
        app.logger.error(f"Error fetching {list_type}: {str(e)}")
        abort(500, description=f"Error fetching {list_type}")