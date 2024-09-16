import json
import os
from ui_client.routes.start import client_interface

from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, current_app

conv = Blueprint("conversation", __name__)

# Dummy conversation list


@conv.route('/conversation-processor', methods=['GET'])
def conversation_processor():
    from ui_client.routes.start import run_setup    # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    return render_template('conversations.html')


# Route to get the list of available conversations
@conv.route('/get-conversations', methods=['GET'])
def get_conversations():
    from ui_client.routes.start import run_setup    # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    threads = ci.cmd_get_thread_list()
    result = []
    for thread in threads:
        result.append({
            "name": thread['ww_thread'].get_thread_name(),
            "id": thread['ww_thread'].get_id()
        })
    # Return the list of conversations as JSON
    return jsonify(result)


# Modified route to get the conversation tree based on the conversation ID
@conv.route('/get-conversation-tree/<conversation_id>', methods=['GET'])
def get_conversation_tree(conversation_id):
    from ui_client.routes.start import run_setup    # import here to avoid circular import
    ci = current_app.config['CLIENT_INTERFACE']
    run_setup(ci)
    tmp = ci.cmd_get_conversation_json(conversation_id)
    # Dummy data for different conversation trees
    # conversation_data = {
    #     1: [
    #         {
    #             "id": "node_1",
    #             "text": "Node 1",
    #             "data": {
    #                 "name": "Node 1",
    #                 "date": "2024-01-01",
    #                 "status": "Active",
    #                 "content": "Editable content for Node 1"
    #             },
    #             "state": { "opened": False},
    #             "children": [
    #                 { "id": "child_1", "text": "Child Node 1", "data": {
    #                     "name": "Child Node 1", "date": "2024-01-02", "status": "Pending", "content": "Editable content for Child Node 1"
    #                 }, "children": False},
    #                 { "id": "child_2", "text": "Child Node 2", "data": {
    #                     "name": "Child Node 2", "date": "2024-01-03", "status": "Completed", "content": "Editable content for Child Node 2"
    #                 }, "children": False}
    #             ]
    #         }
    #     ],
    #     2: [
    #         {
    #             "id": "node_2",
    #             "text": "Node 2",
    #             "data": {
    #                 "name": "Node 2",
    #                 "date": "2024-01-04",
    #                 "status": "Pending",
    #                 "content": "Editable content for Node 2"
    #             },
    #             "state": { "opened": False},
    #             "children": [
    #                 { "id": "child_3", "text": "Child Node 3", "data": {
    #                     "name": "Child Node 3", "date": "2024-01-05", "status": "Pending", "content": "Editable content for Child Node 3"
    #                 }, "children": False}
    #             ]
    #         }
    #     ]
    # }

    # Return the data for the requested conversation, or an empty list if not found
    # conversation_id = 1
    # tmp = jsonify(conversation_data.get(conversation_id, []))
    return jsonify(tmp)
