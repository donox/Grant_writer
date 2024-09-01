def test_assistant(driver):
    print("Running test_assistant")
    print("Getting assistants list:")
    print(driver.test_get_assistants_list())

    new_assistant_data = {
        "name": "Test Assistant",
        "description": "A test assistant",
        "model": "gpt-3.5-turbo"
    }
    print("\nAdding a new assistant:")
    result = driver.test_add_new_assistant(new_assistant_data)
    print(result)

    if result and 'id' in result:
        assistant_id = result['id']

        update_data = {
            "description": "Updated test assistant description"
        }
        print(f"\nUpdating assistant {assistant_id}:")
        print(driver.test_update_assistant(assistant_id, update_data))

        print(f"\nGetting details for assistant {assistant_id}:")
        print(driver.test_get_assistant_details(assistant_id))

        print(f"\nDeleting assistant {assistant_id}:")
        print(driver.test_delete_assistant(assistant_id))
    else:
        print("Failed to create new assistant, skipping further tests.")

    print("Completed test_assistant")
