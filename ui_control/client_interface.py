

class ClientInterface(object):
    def __init__(self, command_processor):
        self.command_processor = command_processor

    def cmd_run_setup(self):
        self.command_processor.cmd_setup({})

    def cmd_get_object_from_id(self, list_type, obj_id):
        result = self.command_processor.cmd_get_object_from_id(list_type, obj_id)
        return result

    def cmd_get_object_from_name(self, list_type, obj_name):
        result = self.command_processor.cmd_get_object_from_id(list_type, obj_name)
        return result

    def cmd_make_thread_json(self, thread_name):
        result = self.command_processor.cmd_make_thread_json(thread_name)
        return result

    def cmd_add_user_message(self, message, thread_name, assistant):
        cmd = {"command": "add_message", "content": message, "role": "user", "thread_name": thread_name,
               "assistant": assistant}
        added_message = self.command_processor.cmd_add_message(cmd)
        return "foo"

    def cmd_update_message(self, message_id, role, thread_name, content):
        foo = 3
        result = self.command_processor.cmd_update_message(message_id, role, thread_name, content)
        return result

    def cmd_process_query(self, user, thread, assistant_id):
        foo = 3
        self.command_processor.cmd_run_query(user, thread, assistant_id)

    def cmd_get_last_results(self, user, thread_name, assistant_id):
        """Get Messages for last query."""
        result = self.command_processor.cmd_get_last_results(user, thread_name, assistant_id)
        return result

    def cmd_get_result_as_text(self, user, thread_name, assistant_id):
        """Get text content of last result."""
        result = self.command_processor.cmd_get_text_responses(user, thread_name, assistant_id)
        return result

    def cmd_get_thread_list(self):
        result = self.command_processor.cmd_get_thread_list()
        return result

    def cmd_get_conversation_json(self, conversation_id):
        result = self.command_processor.cmd_get_conversation_json(conversation_id)
        return result

    def cmd_add_new_thread(self, data):
        result = self.command_processor.cmd_add_new_thread(data)
        return result

    def cmd_get_assistant_list(self):
        result = self.command_processor.cmd_get_assistant_list()
        return result

    def cmd_get_assistant_from_id(self, assistant_id):
        result = self.command_processor.cmd_get_assistant_from_id(assistant_id)
        return result

    def cmd_update_assistant(self, assistant_id, data):
        assistant = self.cmd_get_assistant_from_id(assistant_id)
        if assistant:
            result = assistant.update_assistant(**data)
            return result
        else:
            return False

    def cmd_add_new_assistant(self, data):
        result = self.command_processor.cmd_add_new_assistant(data)
        return result

    def cmd_get_vector_store_list(self):
        result = self.command_processor.cmd_get_vector_store_list()
        return result

    def cmd_add_new_vector_store(self, data):
        result = self.command_processor.cmd_add_new_vector_store(data)
        return result

    def cmd_get_assistant_data(self, assistant_id):
        result = self.command_processor.cmd_get_assistant_data(assistant_id)
        return result
    
    def cmd_get_store_data(self, store_id):
        result = self.command_processor.cmd_get_store_data(store_id)
        return result
    
    def cmd_create_run(self, user,  name, assistant_id):
        result = self.command_processor.cmd_create_run(user, name, assistant_id)
        return result

    def cmd_get_thread_messages(self, thread):
        result = self.command_processor.cmd_get_thread_messages(thread)
        return result

    def cmd_delete_thread(self, thread_id):
        result = self.command_processor.cmd_delete_thread(thread_id)
        return result

    def cmd_delete_assistant(self, assistant_id):
        result = self.command_processor.cmd_delete_assistant(assistant_id)
        return result
    
    def cmd_delete_store(self, store_id):
        result = self.command_processor.cmd_delete_store(store_id)
        return result

    def cmd_update_assistant_instructions(self, assistant_id, instructions):
        result = self.command_processor.cmd_update_assistant_instructions(assistant_id, instructions)
        return result

    def cmd_attach_file(self, assistant_id, file_path):
        result = self.command_processor.cmd_attach_file(assistant_id, file_path)
        return result
