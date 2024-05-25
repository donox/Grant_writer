from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
import json

bp = Blueprint("start", __name__)

# In-memory storage for chat messages
messages = []

#  jstree needs to use AJAX calls - https://www.jstree.com/

# Load your tree data from a JSON file


def load_tree_data():
    with open('Temp/tree_data.json') as f:
        return json.load(f)


@bp.route('/')
def index():
    return render_template('index.html', messages=messages, content=contents[current_index])


@bp.route('/add', methods=['GET', 'POST'])
def add_message():
    if request.method == 'POST':
        message = request.form['message']
        messages.append({'id': len(messages) + 1, 'text': message})
        flash('Message added successfully!', 'success')
        return redirect(url_for('start.index'))
    return render_template('add_message.html')


@bp.route('/edit/<int:message_id>', methods=['GET', 'POST'])
def edit_message(message_id):
    message = next((msg for msg in messages if msg['id'] == message_id), None)
    if not message:
        flash('Message not found!', 'danger')
        return redirect(url_for('start.index'))

    if request.method == 'POST':
        new_text = request.form['message']
        message['text'] = new_text
        flash('Message updated successfully!', 'success')
        return redirect(url_for('start.index'))

    return render_template('edit_message.html', message=message)


@bp.route('/delete/<int:message_id>')
def delete_message(message_id):
    global messages
    messages = [msg for msg in messages if msg['id'] != message_id]
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('start.index'))


@bp.route('/get_tree_data', methods=['GET'])
def get_tree_data():
    # Read the JSON file from the server
    with open('Temp/tree_data.json', 'r') as f:
        tree_data = json.load(f)

    # Return the tree data as JSON
    return jsonify(tree_data)

@bp.route('/tree_data', methods=['GET'])
def tree_data():
    data = load_tree_data()
    return jsonify(data)


# Dummy content list for demonstration purposes
contents = [
    "This is the initial content loaded from the server.",
    "This is the next content.",
    "This is the previous content."
]
current_index = 0


@bp.route('/save', methods=['POST'])
def save():
    global contents, current_index
    text_content = request.form['editor']
    contents[current_index] = text_content
    return jsonify(success=True)


@bp.route('/next', methods=['POST'])
def next_content():
    global current_index
    if current_index < len(contents) - 1:
        current_index += 1
    return jsonify(content=contents[current_index])


@bp.route('/previous', methods=['POST'])
def previous_content():
    global current_index
    if current_index > 0:
        current_index -= 1
    return jsonify(content=contents[current_index])

