# app/models.py
class DataStore:
    def __init__(self):
        self.data = {
            'assistant': {
                '1': {'name': 'Assistant 1', 'specialty': 'General knowledge'},
                '2': {'name': 'Assistant 2', 'specialty': 'Programming'},
            },
            'user': {
                '1': {'name': 'User 1', 'email': 'user1@example.com'},
                '2': {'name': 'User 2', 'email': 'user2@example.com'},
            },
        }