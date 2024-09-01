import subprocess
import time
import requests
import sys
import signal
from test_assistant import test_assistant
from test_thread import test_thread


class FlaskAppDriver:
    def __init__(self, app_file='route_testing/flask_app.py', host='localhost', port=5000):
        self.app_file = app_file
        self.host = host
        self.port = port
        self.base_url = f'http://{host}:{port}'
        self.process = None

    def start_flask_app(self):
        print(f"Starting Flask app from {self.app_file}")
        self.process = subprocess.Popen([sys.executable, self.app_file])
        time.sleep(5)  # Give the server a couple of seconds to start

    def stop_flask_app(self):
        if self.process:
            print("Stopping Flask app")
            self.process.send_signal(signal.SIGINT)
            self.process.wait()

    def get(self, route):
        try:
            response = requests.get(f"{self.base_url}{route}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def post(self, route, data):
        try:
            response = requests.post(f"{self.base_url}{route}", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def delete(self, route):
        try:
            response = requests.delete(f"{self.base_url}{route}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_get_assistants_list(self):
        return self.get('/get-assistants-list/')

    def test_add_new_assistant(self, data):
        return self.post('/add-new-assistant/', data)

    def test_get_assistant_details(self, assistant_id):
        return self.get(f'/get-assistant-details/{assistant_id}')

    def test_update_assistant(self, assistant_id, data):
        return self.post(f'/update-assistant-details/{assistant_id}', data)

    def test_delete_assistant(self, assistant_id):
        return self.delete(f'/delete-assistant/{assistant_id}')


if __name__ == "__main__":
    driver = FlaskAppDriver()

    try:
        driver.start_flask_app()

        # Run tests
        # test_assistant(driver)
        test_thread(driver)
    finally:
        driver.stop_flask_app()