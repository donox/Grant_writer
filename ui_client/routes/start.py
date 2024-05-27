from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
import json
from ui_client.routes.messages import messages, get_initial_message_editor_content

bp = Blueprint("start", __name__)

#  jstree needs to use AJAX calls - https://www.jstree.com/

# Load your tree data from a JSON file
def load_tree_data():
    with open('Temp/tree_data.json') as f:
        return json.load(f)


@bp.route('/')
def index():
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup = current_app.config['RUN_SETUP']    # If first time called, need to set up Assistant
    if run_setup:
        current_app.config['RUN_SETUP'] = False
        ci.cmd_run_setup()
    return render_template('index.html', messages=messages,
                           content=get_initial_message_editor_content())


@bp.route('/add', methods=['GET', 'POST'])
def add_message():
    if request.method == 'POST':
        message = request.form['message']
        messages.append({'id': len(messages) + 1, 'text': message})
        # flash('Message added successfully!', 'success')
        return redirect(url_for('start.index'))
    return render_template('add_message.html')


@bp.route('/edit/<int:message_id>', methods=['GET', 'POST'])
def edit_message(message_id):
    message = next((msg for msg in messages if msg['id'] == message_id), None)
    if not message:
        # flash('Message not found!', 'danger')
        return redirect(url_for('start.index'))

    if request.method == 'POST':
        new_text = request.form['message']
        message['text'] = new_text
        # flash('Message updated successfully!', 'success')
        return redirect(url_for('start.index'))

    return render_template('edit_message.html', message=message)


@bp.route('/delete/<int:message_id>')
def delete_message(message_id):
    global messages
    messages = [msg for msg in messages if msg['id'] != message_id]
    # flash('Message deleted successfully!', 'success')
    return redirect(url_for('start.index'))


@bp.route('/get_tree_data', methods=['GET'])
def get_tree_data():
    # Read the JSON file from the server
    with open('Temp/tree_data.json', 'r') as f:
        tree_data = json.load(f)
    # Return the tree data as JSON
    return jsonify(tree_data)

# @bp.route('/tree_data', methods=['GET'])
# def tree_data():
#     data = load_tree_data()
#     return jsonify(data)





