import json
import os

from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
from urllib.parse import unquote

vect = Blueprint("vector", __name__)


@vect.route('/vector-store-processor')
def vector_store_processor():
    from ui_client.routes.start import run_setup    # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    return render_template('vs.html')


@vect.route("/load-store/", methods=['POST'])
def load_assistant():
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