import subprocess

def execute_curl_command(api_key, vector_store_id):
    """
    Executes a curl command using subprocess to retrieve files from a specified vector store.

    Parameters:
        api_key (str): Your OpenAI API key.
        vector_store_id (str): The ID of the vector store (e.g., 'vs_abc123').

    Returns:
        str: The output from the curl command (the API response).

    Raises:
        Exception: If the curl command fails.
    """
    url = f"https://api.openai.com/v1/vector_stores/{vector_store_id}/files"
    headers = [
        f"Authorization: Bearer {api_key}",
        "Content-Type: application/json",
        "OpenAI-Beta: assistants=v2"
    ]

    # Build the curl command
    cmd = ["curl", url]
    for header in headers:
        cmd.extend(["-H", header])

    try:
        # Execute the command and capture the output
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Handle errors in the subprocess execution
        raise Exception(f"Command failed with error:\n{e.stderr}") from e
