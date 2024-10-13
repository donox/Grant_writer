from flask import abort, request, redirect, url_for, flash, Blueprint, jsonify, current_app
import json
from ui_client.routes.start import client_interface
from assistant.assistant_manager import AssistantManager, Assistant
from assistant.thread_manager import ThreadManager, Thread
from assistant.vector_store_manager import VectorStoreManager, VectorStore

# Blueprint setup for generic routes
gen = Blueprint("generic", __name__)

# Define valid types for list operations
valid_list_types = ['assistants', 'threads', 'stores']


def get_model_class(list_type):
    """
    Retrieves the model class associated with a given list type.
    Allows for both singular and plural forms of list_type.

    Args:
        list_type (str): Type of list (e.g., 'assistant', 'thread', 'store').

    Returns:
        class: Corresponding model class for the list type.

    Raises:
        ValueError: If an invalid list type is provided.
    """
    lt = list_type
    if lt[-1] != 's':
        lt += 's'  # Ensure plural form for lookup
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
    """
    Retrieves the model manager associated with a given list type.

    Args:
        list_type (str): Type of list (e.g., 'assistant', 'thread', 'store').

    Returns:
        Manager instance: The configured manager instance for the list type.

    Raises:
        ValueError: If an invalid list type is provided.
    """
    lt = list_type
    if lt[-1] != 's':
        lt += 's'  # Ensure plural form for lookup
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
    """
    Retrieves an object by name from the specified list type.

    Args:
        list_type (str): The type of list to search within.
        obj_name (str): The name of the object to search for.

    Returns:
        JSON response: The first matching object in JSON format, or None if not found.

    Raises:
        500 Internal Server Error: If an exception occurs during processing.
    """
    model_manager = get_model_manager(list_type)
    try:
        items = model_manager.get_objects_list()
        tmp = jsonify([{'id': item.id, 'name': item.name} for item in items if item.name == obj_name])
        if len(tmp) > 0:
            return tmp[0]
        return None
    except Exception as e:
        abort(500, f"{list_type} with name: {obj_name} not found")


def get_object_from_id_kernel(list_type, obj_id):
    """
    Retrieves an object by ID from the specified list type.

    Args:
        list_type (str): The type of list to search within.
        obj_id (str): The ID of the object to search for.

    Returns:
        JSON response: The object with matching ID in JSON format, or None if not found.

    Raises:
        500 Internal Server Error: If an exception occurs during processing.
    """
    model_manager = get_model_manager(list_type)
    try:
        items = model_manager.get_objects_list()
        tmp = jsonify([{'id': item.id, 'name': item.name} for item in items if item.id == obj_id])
        if len(tmp) > 0:
            return tmp[0]
        return None
    except Exception as e:
        abort(500, f"{list_type} with id: {obj_id} not found")


def check_setup():
    """
    Checks and runs the initial setup for the client interface, avoiding circular imports.
    """
    from ui_client.routes.start import run_setup
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)


@gen.route('/get-<list_type>-list/', methods=['GET'])
def get_list(list_type):
    """
    Endpoint to retrieve a list of all known objects for the specified type.

    Args:
        list_type (str): The type of objects to list (e.g., 'assistants').

    Returns:
        JSON response: A list of all objects with their IDs and names.

    Raises:
        500 Internal Server Error: If an exception occurs during processing.
    """
    check_setup()
    model_manager = get_model_manager(list_type)

    try:
        items = model_manager.get_objects_list()
        return jsonify([{'id': item.id, 'name': item.name} for item in items])
    except Exception as e:
        abort(500, description=f"Error fetching {list_type}: {str(e)}")


@gen.route('/get-<list_type>-object-from_id', methods=['GET'])
def get_object_from_id(list_type, object_id):
    """
    Endpoint to retrieve a specific object by ID for the given list type.

    Args:
        list_type (str): The type of objects.
        object_id (str): The object ID.

    Returns:
        JSON response: The object with the specified ID, or a failure message.
    """
    check_setup()
    result = get_object_from_id_kernel(list_type, object_id)
    if result:
        return result
    return jsonify({'failure': f"No object found with id: {object_id}"})


@gen.route('/get-<list_type>-details/<generic_id>', methods=['GET'])
def get_list_details(list_type, generic_id):
    """
    Endpoint to retrieve detailed information for a specific object by ID.

    Args:
        list_type (str): The type of object.
        generic_id (str): The ID of the object.

    Returns:
        JSON response: Object details in JSON format with a success flag, or a failure message if the object is not found.
    """
    print(f"GET generic endpoint DETAILS: {list_type}, {generic_id}", flush=True)
    check_setup()
    model_manager = get_model_manager(list_type)

    # Attempt to retrieve the model by ID
    # The model is a dict containing a link to the model object
    model_dict = model_manager.get_object_by_id(generic_id)

    # Check if the model was found
    if model_dict is None or not isinstance(model_dict, dict):
        return jsonify({
            "success": False,
            "message": f"No {list_type} found with ID: {generic_id}"
        }), 404  # Return a 404 Not Found status code

    model = model_dict['model']

    # Serialize model to JSON and return with success flag
    res = model.to_json()
    if isinstance(res, dict):
        res["success"] = True
        res['model'] = None         # can't jsonify a python object
        return jsonify(res)

    return jsonify({
        "success": False,
        "message": "Unexpected error retrieving details."
    }), 500  # Return a 500 Internal Server Error for unexpected issues


@gen.route('/get-<list_type>-id-from-name/<object_name>', methods=['GET'])
def get_id_from_name(list_type, object_name):
    """
    Endpoint to retrieve an object's ID by name.

    Args:
        list_type (str): The type of object.
        object_name (str): The name of the object.

    Returns:
        JSON response: Object ID if found, or a failure message.
    """
    check_setup()
    model_manager = get_model_manager(list_type)
    print(f"GET_ID_FROM_NAME: {object_name}")
    model = model_manager.get_object_from_name(object_name)
    if model:
        return jsonify({"success": True, "id": model.get_id()})
    return jsonify(f"failure: model not found")


@gen.route('/update-<list_type>-details/<generic_id>', methods=['GET'])
def update_list_details(list_type, generic_id):
    """
    [Unimplemented] Endpoint to update details for an object by ID.

    Args:
        list_type (str): The type of object.
        generic_id (str): The ID of the object.

    Returns:
        JSON response: Success or failure message.

    Notes:
        - This route is marked as not yet implemented/tested.
    """
    print(f"UPDATE DETAILS: {list_type}, {generic_id}", flush=True)
    check_setup()
    model_manager = get_model_manager(list_type)
    # model = model_manager.get_object_by_id(generic_id)
    data = request.json
    print(f"UPDATE DATA: {data}")
    res = model_manager.update_object_details(generic_id, data)
    if res:
        return jsonify("success: True")
    return jsonify("failure: update failed")

# Unused Generic CRUD Operation Example
# The below section suggests implementing generic CRUD operations.
# It includes example routes for fetching, updating, and deleting various types.
