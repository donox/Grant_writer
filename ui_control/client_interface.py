

class ClientInterface(object):
    def __init__(self, command_processor):
        self.command_processor = command_processor

    def cmd_run_setup(self):
        self.command_processor.cmd_setup({})

    def cmd_add_user_message(self, message):
        cmd = {"command": "add_message", "content": message, "role": "user"}
        added_message = self.command_processor.cmd_add_message(cmd)
        return "foo"

    def cmd_process_query(self):
        self.command_processor.cmd_run_query(None)

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
