import config
from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
import json
from ui_client.routes.start import client_interface

ap = Blueprint("assistant", __name__)


# refactoring of assistant
@ap.route('/assistant-manager-template')
def assistant_manager_template():
    return render_template('assistant_manager.html')


# @ap.route('/update-assistant/<assistant_id>', methods=['POST'])
# def update_assistant(assistant_id):
#     from ui_client.routes.start import run_setup  # import here to avoid circular import
#     ci = current_app.config['CLIENT_INTERFACE']
#     run_setup(ci)
#     data = request.json
#     result = ci.cmd_update_assistant(assistant_id, data)
#     if result:
#         return jsonify({"success": result})
#     else:
#         return jsonify({"error": "Assistant Update Failed"}), 404


# @ap.route('/get-assistant-details/<assistant_id>', methods=['GET'])
# def get_assistant_details(assistant_id):
#     from ui_client.routes.start import run_setup  # import here to avoid circular import
#     ci = current_app.config['CLIENT_INTERFACE']
#     run_setup(ci)
#
#     assistant = ci.cmd_get_assistant_from_id(assistant_id)
#     if assistant:
#         return jsonify(assistant.get_content_data())
#     else:
#         return jsonify({"error": "Assistant not found"}), 404


@ap.route("/assistant-processor")
def assistant_processor():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    return render_template('assistant_processor.html')


@ap.route("/load-assistant/", methods=['POST'])
def load_assistant():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            assistant_id = data['id']
            result = ci.cmd_get_assistant_data(assistant_id)
            return jsonify(result)
        except Exception as e:
            print(f"Failure loading-assistant content: {e.args}")
            return jsonify(failure=f"Failed to load assistant {assistant_id}")


@ap.route("/update-instructions", methods=['POST'])
def update_instructions():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            assistant_id = data["id"]
            instructions = data["instructions"]
            result = ci.cmd_update_assistant_instructions(assistant_id, instructions)
            if result:
                return jsonify(success="Processed " + assistant_id)
            else:
                return jsonify(failure="Did not update " + assistant_id)
        except Exception as e:
            print(f"Fail in updating instructions: {e.args}")
            return jsonify(failure=f"Failed to update instructions for {assistant_id}")


@ap.route("/attach-file", methods=['POST'])
def attach_file():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            assistant_id = data["id"]
            file_path = data["path"]
            result = ci.cmd_attach_file(assistant_id, file_path)
            if result:
                return jsonify(success="Attached " + file_path + " to " + assistant_id)
            else:
                return jsonify(failure="Attach failed " + assistant_id)
        except Exception as e:
            print(f"Fail in attaching file: {e.args}")
            return jsonify(failure=f"Failed to attach file for {assistant_id}")


@ap.route('/delete-assistant/<assistant_id>', methods=['DELETE'])
def delete_assistant(assistant_id):
    ci = client_interface()
    result = ci.cmd_delete_assistant(assistant_id)
    return jsonify({'success': result})

