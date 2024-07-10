import config
from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
import json

bp = Blueprint("start", __name__)


#  jstree needs to use AJAX calls - https://www.jstree.com/


# Load your tree data from a JSON file
def load_tree_data():
    with open('Temp/tree_data.json') as f:
        return json.load(f)


def client_interface():
    return current_app.config['CLIENT_INTERFACE']


def run_setup(ci):
    run_setup = current_app.config['RUN_SETUP']  # If first time called, need to set up Assistant
    if run_setup:
        current_app.config['RUN_SETUP'] = False
        ci.cmd_run_setup()


@bp.route('/')
def index():
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    return render_template('index.html')


@bp.route('/setup-run', methods=['POST'])
def setup_run():
    ci = current_app.config['CLIENT_INTERFACE']
    if request.method == 'POST':
        user = request.form['user']
        thread_id = request.form['thread_id']
        run_setup(ci)
        return render_template('index.html', messages="",
                               content=" ")


@bp.route('/get-thread-list/<user>', methods=['GET'])
def get_thread_list(user):
    ci = client_interface()
    run_setup(ci)
    tmp = ci.cmd_get_thread_list(user)
    result = []
    for r in tmp:  # remove references to thread object which cannot be jsonified.
        r_copy = r.copy()
        r_copy["ww_thread"] = None
        result.append(r_copy)
    return jsonify(result)


@bp.route('/get-assistant-list/', methods=['GET'])
def get_assistant_list():
    ci = client_interface()
    run_setup(ci)
    result = ci.cmd_get_assistant_list()
    result.insert(0, {'name': 'NEW ASSISTANT', 'id': '-----'})
    return jsonify(result)


@bp.route('/add-new-thread/<user>', methods=['POST'])
def add_new_thread(user):
    ci = client_interface()
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads([x for x in request.form.items()][0][0])
            data['user'] = user
        except Exception as e:
            print(f"Error decoding json from add thread: {e}")
            return render_template('index.html')
        result = ci.cmd_add_new_thread(data)
        if result:
            flash('Conversation file updated', 'success')
        else:
            flash('Failure updating conversation file', 'danger')
        return jsonify(result)


@bp.route('/add-new-assistant/', methods=['POST'])
def add_new_assistant():
    ci = client_interface()
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads([x for x in request.form.items()][0][0])
        except Exception as e:
            print(f"Error decoding json from add thread: {e}")
            return render_template('index.html')
        result = ci.cmd_add_new_assistant(data)
        foo = 3
        return render_template('index.html')  # This a reasonable thing to do????


# Switch page to query view
@bp.route('/switch-to-query/', methods=['POST'])
def switch_to_query():
    ci = client_interface()
    # TODO:  After switching to a query, need to load existing content.
    assistant_id = current_app.config['ASSISTANT']  # !!!!! TEMPORARY TILL ACTUAL SELECTION
    data = None
    if request.method == 'POST':
        try:
            thread_name = request.json.get('name');  # Use request.json to get JSON data
            user = request.json.get('user')
        except Exception as e:
            print(f"Error decoding json from add thread: {e}")
            return render_template('index.html')
    tmplt = jsonify({'redirectUrl': url_for('message.query_processor',
                                            name=thread_name,
                                            user=user,
                                            assistant=assistant_id)})
    return tmplt


# Switch page to assistant view
@bp.route('/switch-to-assistant/', methods=['POST'])
def switch_to_assistant():
    ci = client_interface()
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            assistant_name = data['name']
            assistant_id =data['id']
        except Exception as e:
            print(f"Error decoding json from add thread: {e}")
            return render_template('index.html')
    tmplt = jsonify({'redirectUrl': url_for('assistant_page.assistant_processor'),
                     'name': assistant_name,
                     'assistant': assistant_id})
    return tmplt


@bp.route('/delete-thread', methods=['POST'])
def delete_thread():
    ci = client_interface()
    if request.method == 'POST':
        threadName = request.form.get('text')
        result = ci.cmd_delete_thread(threadName)
        if result:
            return render_template('index.html', messages="", content=" ")
        else:
            return jsonify(success=f"Failed to delete {threadName}")


@bp.route('/delete-assistant', methods=['POST'])
def delete_assistant():
    ci = client_interface()
    if request.method == 'POST':
        assistant_id = request.form.get('text')
        result = ci.cmd_delete_assistant(assistant_id)
        if result:
            return render_template('index.html', messages="", content=" ")
        else:
            return jsonify(success=f"Failed to delete assistant {assistant_id}")

# @bp.route('/add', methods=['GET', 'POST'])
# def add_message():
#     if request.method == 'POST':
#         message = request.form['message']
#         messages.append({'id': len(messages) + 1, 'text': message})
#         # flash('Message added successfully!', 'success')
#         return redirect(url_for('start.index'))
#     return render_template('add_message.html')


# @bp.route('/edit/<int:message_id>', methods=['GET', 'POST'])
# def edit_message(message_id):
#     message = next((msg for msg in messages if msg['id'] == message_id), None)
#     if not message:
#         # flash('Message not found!', 'danger')
#         return redirect(url_for('start.index'))
#
#     if request.method == 'POST':
#         new_text = request.form['message']
#         message['text'] = new_text
#         # flash('Message updated successfully!', 'success')
#         return redirect(url_for('start.index'))
#
#     return render_template('edit_message.html', message=message)
#
#
# @bp.route('/delete/<int:message_id>')
# def delete_message(message_id):
#     global messages
#     messages = [msg for msg in messages if msg['id'] != message_id]
#     # flash('Message deleted successfully!', 'success')
#     return redirect(url_for('start.index'))
#
#
# @bp.route('/get_tree_data', methods=['GET'])
# def get_tree_data():
#     # Read the JSON file from the server
#     with open('Temp/tree_data.json', 'r') as f:
#         tree_data = json.load(f)
#     # Return the tree data as JSON
#     return jsonify(tree_data)

# @bp.route('/tree_data', methods=['GET'])
# def tree_data():
#     data = load_tree_data()
#     return jsonify(data)
