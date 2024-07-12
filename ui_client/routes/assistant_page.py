import config
from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
import json

ap = Blueprint("assistant_page", __name__)


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
