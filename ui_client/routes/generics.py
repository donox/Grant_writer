from flask import abort,  request, redirect, url_for, flash, Blueprint, jsonify, current_app
import json
from ui_client.routes.start import client_interface
from assistant.assistant_manager import AssistantManager,  Assistant
from assistant.thread_manager import ThreadManager, Thread
from assistant.vector_store_manager import VectorStoreManager, VectorStore

gen = Blueprint("generic", __name__)
valid_list_types = ['assistants', 'threads', 'stores']


def get_model_class(list_type):
    lt = list_type    # allow model to be singular or plural
    if lt[-1] != 's':
        lt = lt + 's'
    model_mapping = {
        'assistants': Assistant,
        'threads': Thread,
        'stores': VectorStore
    }
    if lt in model_mapping:
        return model_mapping.get(lt)
    else:
        raise ValueError(f"Invalid Model type: {list_type}")


def get_model_manager(list_type):
    lt = list_type    # allow model to be singular or plural
    if lt[-1] != 's':
        lt = lt + 's'
    model_mapping = {
        'assistants': 'ASSISTANT_MANAGER',
        'threads': 'THREAD_MANAGER',
        'stores': 'STORE_MANAGER'
    }
    if lt in model_mapping:
        return current_app.config[model_mapping[lt]]
    else:
        raise ValueError(f"Invalid Model Manager type: {list_type}")


def get_object_from_name_kernel(list_type, obj_name):
    model_manager = get_model_manager(list_type)
    try:
        items = model_manager.get_objects_list()
        tmp = jsonify([{'id': item.id, 'name': item.name} for item in items if item.name == obj_name])
        if len(tmp) > 0:
            return tmp[0]
        return None
    except Exception as e:
        abort(500, f"{list_type}  with name: {obj_name} not found", )


def get_object_from_id_kernel(list_type, obj_id):
    model_manager = get_model_manager(list_type)
    try:
        items = model_manager.get_objects_list()
        tmp = jsonify([{'id': item.id, 'name': item.name} for item in items if item.id == obj_id])
        if len(tmp) > 0:
            return tmp[0]
        return None
    except Exception as e:
        abort(500, f"{list_type}  with id: {obj_id} not found", )


def check_setup():
        from ui_client.routes.start import run_setup  # import here to avoid circular import
        ci = current_app.config['CLIENT_INTERFACE']
        run_setup(ci)


@gen.route('/get-<list_type>-list/', methods=['GET'])
def get_list(list_type):
    """Create a list of all known objects of the specified type. """
    check_setup()
    model_manager = get_model_manager(list_type)

    try:
        items = model_manager.get_objects_list()
        return jsonify([{'id': item.id, 'name': item.name} for item in items])
    except Exception as e:
        # app.logger.error(f"Error fetching {list_type}: {str(e)}")  # TODO: Logger
        abort(500, description=f"Error fetching {list_type}: {str(e)}")


@gen.route('/get-<list_type>-object-from_id', methods=['GET'])
def get_object_from_id(list_type, object_id):
    check_setup()
    result = get_object_from_id_kernel(list_type, object_id)
    if result:
        return result
    return jsonify({'failure': f"No object found with id: {object_id}" })


@gen.route('/get-<list_type>-details/<generic_id>', methods=['GET'])
def get_list_details(list_type, generic_id):
    """Get details as provided by OAI for a specified object."""
    print(f"GET generic endpoint DETAILS: {list_type}, {generic_id}", flush=True)
    check_setup()
    model_manager = get_model_manager(list_type)
    model = model_manager.get_object_by_id(generic_id)
    res = model.to_json()

    if type(res) is dict:
        res["success"] = True
        tmp = jsonify(res)
        return tmp
    else: 
        return jsonify(f"failure: unable to get details")


@gen.route('/get-<list_type>-id-from-name/<object_name>', methods=['GET'])
def get_id_from_name(list_type, object_name):
    """Given a named object, find its id. """
    check_setup()
    model_manager = get_model_manager(list_type)
    print(f"GET_ID_FROM_NAME: {object_name}")
    model = model_manager.get_object_from_name(object_name)
    if model:
        tmp = jsonify({"success": True, "id": model.get_id()})
        print(f"JSONIFY RESULT: {tmp}", flush=True)
        return tmp
    else:
        return jsonify(f"failure: model not found")


# NOT YET IMPLEMENTED/TESTED
@gen.route('/update-<list_type>-details/<generic_id>', methods=['GET'])
def update_list_details(list_type, generic_id):
    print(f"UPDATE xx DETAILS: {list_type}, {generic_id}", flush=True)
    check_setup()
    model_manager = get_model_manager(list_type)
    model = model_manager.get_object_by_id(generic_id)
    data = request.json
    print(f"UPDATE DATA: {data}")
    res = model_manager.update_object_details(generic_id, data)
    print(f"UPDATED: {json.loads(model.to_json())}")
    if res:
        return jsonify("success: True")
    return jsonify("failure: update failed")

# MAKE MORE GENERIC
# # Dictionary to store our "database" of various types
# data = {
#     'assistant': {
#         '1': {'name': 'Assistant 1', 'specialty': 'General knowledge'},
#         '2': {'name': 'Assistant 2', 'specialty': 'Programming'},
#     },
#     'user': {
#         '1': {'name': 'User 1', 'email': 'user1@example.com'},
#         '2': {'name': 'User 2', 'email': 'user2@example.com'},
#     },
# }
#
# @gen.route('/<function>/<list_type>/<generic_id>', methods=['GET', 'PUT', 'DELETE'])
# def generic_operation(function, list_type, generic_id):
#     if list_type not in data or generic_id not in data[list_type]:
#         return jsonify({'error': f'{list_type.capitalize()} not found'}), 404
#
#     if function == 'get':
#         return jsonify(data[list_type][generic_id])
#     elif function == 'update' and request.method == 'PUT':
#         data[list_type][generic_id].update(request.json)
#         return jsonify(data[list_type][generic_id])
#     elif function == 'delete' and request.method == 'DELETE':
#         deleted_item = data[list_type].pop(generic_id)
#         return jsonify(deleted_item)
#     else:
#         return jsonify({'error': 'Invalid operation'}), 400

# EXAMPLE CALLS:
# self.get('/get/assistant/1')  # Get assistant 1
# self.put('/update/user/2', json={"name": "Updated User 2"})  # Update user 2
# self.delete('/delete/assistant/1')  # Delete assistant 1






