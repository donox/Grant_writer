import config
from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app
import json
from ui_client.routes.start import client_interface

thr = Blueprint("thread", __name__)


# refactoring of thread
@thr.route('/thread-manager-template')
def thread_manager_template():
    return render_template('thread_manager.html')


@thr.route('/update-thread/<thread_id>', methods=['POST'])
def update_thread(thread_id):
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    data = request.json
    success = ci.cmd_update_thread(thread_id, data)
    return jsonify({"success": success})


# @thr.route('/get-thread-details/<id_type>/<thread_ident>', methods=['GET'])
# def get_thread_details(id_type, thread_ident):
#     from ui_client.routes.start import run_setup  # import here to avoid circular import
#     ci = current_app.config['CLIENT_INTERFACE']
#     run_setup(ci)
#     print("OLD GET THREAD")
#     idt = str.lower(id_type)
#     if idt == 'id':
#         thread = ci.cmd_get_object_from_id("threads", thread_ident)  # remove model finder from generic route and make available here
#     elif idt == 'name':
#         thread = ci.cmd_get_object_from_name("threads", thread_ident)
#     else:
#         return jsonify({"error": f"invalid thread type: {id_type}, must be 'name' or 'id'"})
#
#     if thread:
#         return jsonify(thread.get_content_data())
#     else:
#         return jsonify({"error": "thread not found"}), 404


# end refactoring


@thr.route("/thread-processor/")
def thread_processor():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    return render_template('thread_processor.html')


@thr.route("/load-thread/", methods=['POST'])
def load_thread():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            thread_id = data['id']
            result = ci.cmd_get_thread_data(thread_id)
            return jsonify(result)
        except Exception as e:
            print(f"Failure loading-thread content: {e.args}")
            return jsonify(failure=f"Failed to load thread {thread_id}")


@thr.route("/update-instructions/", methods=['POST'])
def update_instructions():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            thread_id = data["id"]
            instructions = data["instructions"]
            result = ci.cmd_update_thread_instructions(thread_id, instructions)
            if result:
                return jsonify(success="Processed " + thread_id)
            else:
                return jsonify(failure="Did not update " + thread_id)
        except Exception as e:
            print(f"Fail in updating instructions: {e.args}")
            return jsonify(failure=f"Failed to update instructions for {thread_id}")


@thr.route("/attach-file", methods=['POST'])
def attach_file():
    from ui_client.routes.start import run_setup  # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    if request.method == 'POST':
        try:
            data = json.loads(request.data)
            thread_id = data["id"]
            file_path = data["path"]
            result = ci.cmd_attach_file(thread_id, file_path)
            if result:
                return jsonify(success="Attached " + file_path + " to " + thread_id)
            else:
                return jsonify(failure="Attach failed " + thread_id)
        except Exception as e:
            print(f"Fail in attaching file: {e.args}")
            return jsonify(failure=f"Failed to attach file for {thread_id}")


@thr.route('/delete-thread/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    ci = client_interface()
    result = ci.cmd_delete_thread(thread_id)
    return jsonify({'success': result})

