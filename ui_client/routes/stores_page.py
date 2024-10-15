import json
import os
from ui_client.routes.start import client_interface

from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
from urllib.parse import unquote

vect = Blueprint("vector", __name__)


@vect.route('/vector-store-processor')
def vector_store_processor():
    from ui_client.routes.start import run_setup    # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    return render_template('store_processor.html')


@vect.route("/load-store/", methods=['POST'])
def load_assistant():                                     # !!!! BROKEN NAME - is this route used???????
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            store_id = data['id']
            result = ci.cmd_get_store_data(store_id)
            return jsonify(result)
        except Exception as e:
            print(f"Failure loading-store content: {e.args}")
            return jsonify(failure=f"Failed to load store {store_id}")


@vect.route('/remove-vector-store-files', methods=['POST'])
def remove_vector_store_files():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)

    data = request.get_json()
    file_ids = data.get('files', [])
    store_id = data.get('store_id')

    # Ensure both store_id and file_ids are provided
    if not store_id or not file_ids:
        return jsonify({"success": False, "error": "Missing store_id or files"}), 400

    # Call the function from client_interface
    success = ci.cmd_remove_files_from_vector_store(store_id, file_ids)

    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Failed to remove files"}), 500


@vect.route('/delete-store/<store_id>', methods=['DELETE'])
def delete_thread(store_id):
    ci = client_interface()
    result = ci.cmd_delete_store(store_id)
    return jsonify({'success': result})
