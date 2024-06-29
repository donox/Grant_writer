

class ClientInterface(object):
    def __init__(self, command_processor):
        self.command_processor = command_processor
        foo = 3

    def cmd_run_setup(self):
        self.command_processor.cmd_setup({})
        foo = 3

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

    # def cmd_add_and_process_query(self, message):         # UNUSED???
    #     self.cmd_add_user_message(message)
    #     self.cmd_process_query()
    #     results = self.cmd_get_last_results()
    #     return results

    def cmd_get_thread_list(self, user):
        result = self.command_processor.cmd_get_thread_list(user)
        return result

    def cmd_add_new_thread(self, data):
        result = self.command_processor.cmd_add_new_thread(data)
        return result

    def cmd_get_assistant_list(self):
        result = self.command_processor.cmd_get_assistant_list()
        return result

    def cmd_add_new_assistant(self, data):
        result = self.command_processor.cmd_add_new_assistant(data)
        return result

    def cmd_create_run(self, user,  name, assistant_id):
        result = self.command_processor.cmd_create_run(user, name, assistant_id)
        return result

    def cmd_get_thread_messages(self, thread):
        result = self.command_processor.cmd_get_thread_messages(thread)
        return result

    def cmd_delete_thread(self, thread_name):
        result = self.command_processor.cmd_delete_thread(thread_name)
        return result

    def cmd_delete_assistant(self, assistand_id):
        result = self.command_processor.cmd_delete_assistant(assistand_id)
        return result
