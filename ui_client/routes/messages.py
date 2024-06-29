from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
from urllib.parse import unquote

msg = Blueprint("message", __name__)


@msg.route('/query_processor')
def query_processor():
    from ui_client.routes.start import run_setup    # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    return render_template('query_processor.html')


@msg.route('/init_thread/<thread>', methods=['POST'])
def init_thread(thread):
    ci = current_app.config['CLIENT_INTERFACE']
    message_list = ci.cmd_get_thread_messages(thread)
    # if len(message_list) != 1:
    #     raise ValueError(f"Unexpected message list: {message_list}")
    print(f"INIT Message list length: {len(message_list)}")
    if type(message_list) is list and len(message_list) > 0:
        content = message_list[0].get_content()
    else:
        content = "No content found as yet."
    return jsonify(content=content, success=True)


@msg.route('/query', methods=['POST'])
def run_query():
    ci = current_app.config['CLIENT_INTERFACE']
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    run_setup(ci)
    ci = current_app.config['CLIENT_INTERFACE']
    if request.method == 'POST':
        # TODO: if content is empty, need to just update the message list (likely not on screen) and, possibly,
        # indicate that nothing was run.
        msg_text = request.form.get('content')
        user = request.form.get('user')
        thread_name = request.form.get('thread')
        assistant_id = request.form.get('assistant')
        if 'urlencoded' in request.content_type:
            msg_text = unquote(msg_text)
        else:
            print(f"/query content has content type: {request.content_type}")  # Probably will need json at a min
        if not msg_text:
            flash("Message text mst be non-empty", "fail")
            return jsonify("failure")

        # If the user update an existing message (nothing new is added).  If the user updated an assistant response
        # message, it becomes a user message (??). [should it be moved/duplicated to the end of the convesation?]
        ci.cmd_add_user_message(msg_text, thread_name, assistant_id)
        ci.cmd_process_query(user, thread_name, assistant_id)      # user, name, assistant_id

        results = ci.cmd_get_last_results(user, thread_name, assistant_id)   # List of Messages
        result_list = []
        for result in results:
            rslt = result.get_content_dict()
            rslt['thread'] = thread_name
            result_list.append(rslt)

        return jsonify(result_list)
    else:
        raise RuntimeError("Failure on /query POST")      # NEED TO CONTINUE EXECUTION


@msg.route('/update-message', methods=['POST'])
def update_message():
    ci = current_app.config['CLIENT_INTERFACE']
    if request.method == 'POST':
        message_id = request.form.get('message_id')
        role = request.form.get('role')
        thread_name = request.form.get('thread')
        content = request.form.get('content')
        if 'urlencoded' in request.content_type:
            content = unquote(content)
    result = ci.cmd_update_message(message_id, role, thread_name, content)
    return jsonify(success=result)


@msg.route('/save', methods=['POST'])
def save():
    # global contents, current_index
    # text_content = request.form['editor']
    # contents[current_index] = text_content
    return jsonify(success=True)
