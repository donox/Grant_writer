

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

    def cmd_process_query(self, user, thread, assistant_id):
        self.command_processor.cmd_run_query(user, thread, assistant_id)

    def cmd_get_last_results(self):
        """Get MessageManager for last query."""
        result = self.command_processor.cmd_get_last_results()
        return result

    def cmd_get_result_as_text(self):
        """Get text content of last result."""
        result = self.command_processor.cmd_get_text_responses()
        return result

    def cmd_add_and_process_query(self, message):
        self.cmd_add_user_message(message)
        self.cmd_process_query()
        results = self.cmd_get_last_results()
        return results

    def cmd_get_thread_list(self, user):
        result = self.command_processor.cmd_get_thread_list(user)
        return result

    def cmd_add_new_thread(self, data):
        result = self.command_processor.cmd_add_new_thread(data)
        return result

    def cmd_create_run(self, user,  name, assistant_id):
        result = self.command_processor.cmd_create_run(user, name, assistant_id)
        return result

    def cmd_get_thread_messages(self, thread):
        result = self.command_processor.cmd_get_thread_messages(thread)
        return result
