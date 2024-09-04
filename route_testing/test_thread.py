import json
import random


def test_thread(driver):
    print("\n--- Testing Thread Routes ---")

    # Test adding a new thread
    new_thread_data = {
        "name": "Test Thread " + str(random.randint(1, 1000)),  # possible (unlikely) name clash
        "purpose": "Testing thread operations",
        "user": "TestUser"
    }
    result = driver.post('/add-new-thread/', new_thread_data)
    print(f"ADD THREAD: {result}")

    if result and result.get('success'):
        thread_name = new_thread_data['name']

        # Test getting thread details
        print(f"\nGetting details for thread {thread_name}:")
        thread_id_json = driver.get(f'/get-thread-id-from-name/{thread_name}')
        if thread_id_json and 'success' in thread_id_json and thread_id_json['success']:
            thread_id = thread_id_json['id']
            thread_details = driver.get(f'/get-thread-details/{thread_id}')
            print(thread_details)
        else:
            print("Failed to get thread ID")

        if thread_details and 'id' in thread_details:
            thread_id = thread_details['id']

            # Test updating thread
            update_data = {
                "purpose": "Updated test thread purpose"
            }
            #   UPDATE THREAD NOT YET IMPLEMENTED - is this the same as add message to thread?????
            #    NOTE:  there may be updates to the OAI object and separately to the model object.  DO
            #           we need to discriminate????
            # print(f"\nUpdating thread {thread_id}:")
            # update_result = driver.post(f'/update-thread/{thread_id}', update_data)
            # print(update_result)
            #
            # # Test getting updated thread details
            # print(f"\nGetting updated details for thread {thread_name}:")
            # updated_thread_details = driver.get(f'/get-thread-details/{thread_id}')
            # print(updated_thread_details)

            # Test deleting thread
            print(f"\nDeleting thread {thread_id}:")
            delete_result = driver.delete(f'/delete-thread/{thread_id}')
            print(delete_result)

            # Verify thread deletion
            print(f"\nAttempting to get details of deleted thread {thread_name}:")
            deleted_thread_details = driver.get(f'/get-thread-details/{thread_name}')
            if deleted_thread_details.get('error'):
                print("Thread successfully deleted.")
            else:
                print("Warning: Thread may not have been deleted.")
        else:
            print("Failed to get thread details, skipping update and delete tests.")
    else:
        print("Failed to create new thread, skipping further tests.")

    # Test getting all threads
    print("\nGetting all threads:")
    all_threads = driver.get('/get-threads-list/')
    print(all_threads)