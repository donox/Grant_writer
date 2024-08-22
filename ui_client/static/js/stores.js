//assistants.js


function loadStoreDetails(storeId, isNew) {
    fetch(`/get-store-details/${storeId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            displayStoreDetails(data);
        })
        .catch(error => console.error('Error loading store details:', error));
}


function displayStoreDetails(store) {
    $('#storeDetails').show();
    $('#storeName').val(store.name);
    $('#storeId').val(store.id);
    $('#storeInstructions').val(store.instructions);

    // Add more fields as necessary
}

function clearStoreDetails() {
    $('#storeName').text('');
    $('#storeId').text('');
    $('#storeInstructions').val('');
    // Clear more fields as necessary

    // Hide the store details section
    $('#storeDetails').hide();
}

function updateStoreDetails() {
    let storeId = $('#storeId').val();
    let updatedData = {
        name: $('#storeName').val(),
        instructions: $('#storeInstructions').val(),
        // Add more fields as necessary
    };

    fetch(`/update-store/${storeId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Store updated successfully');
                get_list_of_stores(); // Refresh the list
            } else {
                alert('Failed to update store: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error updating store:', error);
            alert('An error occurred while updating the store');
        });
}

function deleteStore(storeId) {
    if (confirm('Are you sure you want to delete this store?')) {
        fetch(`/delete-store/${storeId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Store deleted successfully');
                    getList('stores'); // Refresh the list
                } else {
                    alert('Failed to delete store: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error deleting store:', error);
                alert('An error occurred while deleting the store');
            });
    }
}


function openStorePopup(prohibitedNames, callback) {
// Show the popup
    $('#popupStoreOverlay, #popupStoreForm').show();

    // Clear any previous input
    $('#storeNameInput').val('');

    // Handle form submission
    $('#storeSubmitBtn').off('click').on('click', function () {
        let name = $('#storeNameInput').val().trim();

        if (prohibitedNames.includes(name)) {
            alert('This name is not allowed. Please choose a different name.');
            return;
        }

        if (name) {
            // Hide the popup
            $('#popupStoreOverlay, #popupStoreForm').hide();

            // Call the callback with the new store data
            callback({name: name});
        } else {
            alert('Please enter a name for the new store.');
        }
    });

    // Handle popup close
    $('#storeCloseBtn').off('click').on('click', function () {
        $('#popupStoreOverlay, #popupStoreForm').hide();
    });
}

// function addStore(storeData) {
//     fetch('/add-new-store/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(storeData)
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert('New store added successfully');
//                 get_list('stores'); // Refresh the list
//             } else {
//                 alert('Failed to add new store');
//             }
//         })
//         .catch(error => console.error('Error adding new store:', error));
// }


// Export functions if using modules
// export {
//     loadAssistantDetails,
//     displayAssistantDetails,
//     updateAssistantDetails,
//     deleteAssistant,
//     openAssistantPopup,
//     addAssistant
// };