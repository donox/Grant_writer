from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
from urllib.parse import unquote


msg = Blueprint("message", __name__)

# In-memory storage for chat messages
messages = []

# Dummy content list for demonstration purposes
contents = [
    "This is the initial content loaded from the server.",
    "This is the next content.",
    "This is the previous content."
]
current_index = 0


@msg.route('/query_processor')
def query_processor():
    return render_template('query_processor.html')


@msg.route('/init_thread/<thread>', methods=['POST'])
def init_thread(thread):
    foo = 3
    return jsonify(success=True)


@msg.route('/save', methods=['POST'])
def save():
    # global contents, current_index
    # text_content = request.form['editor']
    # contents[current_index] = text_content
    return jsonify(success=True)


@msg.route('/next', methods=['POST'])
def next_content():
    global current_index
    if current_index < len(contents) - 1:
        current_index += 1
    return jsonify(content=contents[current_index])


@msg.route('/previous', methods=['POST'])
def previous_content():
    global current_index
    if current_index > 0:
        current_index -= 1
    res = jsonify(content=contents[current_index])
    return res


@msg.route('/query/<thread>', methods=['POST'])
def run_query(thread):
    ci = current_app.config['CLIENT_INTERFACE']
    if request.method == 'POST':
        msg_text = request.form.get('content')
        if 'urlencoded' in request.content_type:
            msg_text = unquote(msg_text)
        else:
            print(f"/query content has content type: {request.content_type}")  # Probably will need json at a min
        # flash('Message updated successfully!', 'success')
        ci.cmd_add_user_message(msg_text)
        ci.cmd_process_query()
        result = ci.cmd_get_result_as_text()
        return jsonify({'content': result})
    else:
        raise RuntimeError("Failure on /query POST")      # NEED TO CONTINUE EXECUTION




def get_initial_message_editor_content():
    return contents[current_index]
