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
            // Show the button and vector store content section for the selected store
            $('#removeSelectedFilesBtn').show();
            $('#vectorStoreContent').show();
            displayStoreDetails(data);
        })
        .catch(error => console.error('Error loading store details:', error));
}
// function which turns off the Store Details info if there is no displayed store.
// (currently not called)
function resetStoreSelection() {
    $('#removeSelectedFilesBtn').hide();
    $('#vectorStoreContent').hide();
}


function displayStoreDetails(store) {
    $('#storeDetails').show();
    const form = $('#storeForm');
    let formContent = '';
    listConfigs.stores.detailFields.forEach(field => {
        const fieldHtml = createFieldHtml(field, store[field.name]);
        formContent += fieldHtml;
    });
    form.html(formContent);
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
    $('#popupStoreOverlay, #popupStoreOverlay').show();

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

function fetchFileList(directory) {
    fetch(`/store_list_files?dir=${encodeURIComponent(directory)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Network response was not ok (${response.statusText})`);
            }
            return response.json();
        })
        .then(data => {
            if (data.files) {
                displayStoreFileList(data.files);
            } else {
                console.error('No files found:', data);
            }
        })
        .catch(error => {
            console.error('Error fetching file list:', error);
        });
}

function displayStoreFileList(files) {
    // Create a Bootstrap list group
    var listGroup = $('<ul class="list-group"></ul>');

    // Iterate over the files and create list items
    files.forEach(function (file) {
        var listItem = $('<li class="list-group-item"></li>').text(file);
        listGroup.append(listItem);
    });

    // Append the list to a container in your HTML
    $('#store-file-list').html(listGroup);
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
// Toggle visibility of Stores and StoreDetails sections
document.addEventListener('DOMContentLoaded', function () {
    const storesHeader = document.getElementById('storesHeader');
    const storeDetailsHeader = document.getElementById('storeDetailsHeader');
    const storesSection = document.getElementById('storesSection');
    const storeDetailsSection = document.getElementById('storeDetailsSection');

    storesHeader.addEventListener('click', function () {
        if (storesSection.style.display === 'none') {
            storesSection.style.display = 'block';
        } else {
            storesSection.style.display = 'none';
        }
    });

    storeDetailsHeader.addEventListener('click', function () {
        if (storeDetailsSection.style.display === 'none') {
            storeDetailsSection.style.display = 'block';
        } else {
            storeDetailsSection.style.display = 'none';
        }
    });
});

// Initialize jsTree for Vector Store Content
$(document).ready(function () {

    // Handle removal of selected files when the button is clicked
    $('#removeSelectedFilesBtn').on('click', function () {
        let selectedFiles = $('#fileTree').jstree('get_selected');

        if (selectedFiles.length === 0) {
            alert('No files selected for removal.');
            return;
        }

        // Send the selected file IDs to the backend for removal
        $.ajax({
            url: '/remove-vector-store-files',  // The backend should handle this endpoint
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({files: selectedFiles}),
            success: function (response) {
                if (response.success) {
                    alert('Selected files removed successfully.');
                    $('#fileTree').jstree('refresh');  // Refresh the jsTree to update the file list
                } else {
                    alert('Error removing files.');
                }
            },
            error: function () {
                alert('An error occurred while trying to remove files.');
            }
        });
    });
});