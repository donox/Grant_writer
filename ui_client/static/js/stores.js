

/**
 * Displays the details of a store by populating a form with its fields.
 * @param {Object} store - The store object containing details to display.
 */
function displayStoreDetails(store) {
    $('#storeDetails').show();
    $('#vectorStoreContent').show();
    initializeJsTree(store.files); // Assume data.files is already in jsTree-compatible format
}

/**
 * Clears the store details from the form and hides the store details section.
 * Useful for resetting the UI when switching between stores or on delete.
 */
function clearStoreDetails() {
    $('#storeName').text('');
    $('#storeId').text('');
    $('#storeInstructions').val('');
    // Add more fields as necessary to clear other store details
    $('#storeDetails').hide();
}

/**
 * Updates the details of a store using the current form values.
 */
function updateStoreDetails() {
    let storeId = $('#storeId').val();
    let updatedData = {
        name: $('#storeName').val(),
        instructions: $('#storeInstructions').val(),
        // Include additional fields as necessary
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
            get_list_of_stores(); // Refresh the store list
        } else {
            alert('Failed to update store: ' + (data.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error updating store:', error);
        alert('An error occurred while updating the store');
    });
}

// /**   SUPERCEDED BY GENERIC GET_LIST_DETAILS
//  * Loads the details of a specified store and initializes jsTree to display its contents.
//  * @param {string} storeId - The ID of the store to load.
//  */
// function loadStoreDetails(storeId) {
//     fetch(`/get-store-details/${storeId}`, {
//         method: 'GET',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//     })
//     .then(response => response.json())
//     .then(data => {
//         $('#vectorStoreContent').show();
//         initializeJsTree(data.files); // Assume data.files is already in jsTree-compatible format
//     })
//     .catch(error => console.error('Error loading store details:', error));
// }

/**
 * Initializes jsTree with the provided data and enables checkbox selection.
 * @param {Array} treeData - Data formatted for jsTree with checkboxes.
 */
function initializeJsTree(treeData) {
    $('#fileTree').jstree("destroy").empty();  // Reset the jsTree if it was previously initialized
    $('#fileTree').jstree({
        'core': {
            'data': treeData
        },
        'plugins': ['checkbox']
    });
}


/**
 * Deletes a store after user confirmation.
 * @param {string} storeId - The ID of the store to delete.
 */
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

/**
 * Opens a popup to create a new store, with form validation for prohibited names.
 * @param {Array} prohibitedNames - List of names that are not allowed.
 * @param {function} callback - Callback function to execute after a successful creation.
 */
// function openStorePopup(prohibitedNames, callback) {
//     $('#popupStoreOverlay, #popupStoreOverlay').show();
//     $('#storeNameInput').val('');
//
//     $('#storeSubmitBtn').off('click').on('click', function () {
//         let name = $('#storeNameInput').val().trim();
//         if (prohibitedNames.includes(name)) {
//             alert('This name is not allowed. Please choose a different name.');
//             return;
//         }
//         if (name) {
//             $('#popupStoreOverlay, #popupStoreForm').hide();
//             callback({name: name});
//         } else {
//             alert('Please enter a name for the new store.');
//         }
//     });
//
//     $('#storeCloseBtn').off('click').on('click', function () {
//         $('#popupStoreOverlay, #popupStoreForm').hide();
//     });
// }


/**
 * Displays a list of files using jstree.
 * @param {Array} files - List of file objects, each with 'name' and 'id'.
 *
 * This function *may* be invoked by inclusion in config.js/stores/displayDetails.  Should not
 * be used if content displayed as jstree.
 */
function displayStoreFileList(files) {
    const listGroup = $('<ul class="list-group"></ul>');
    files.forEach(function (file) {
        const listItem = $('<li class="list-group-item"></li>').text(file.name);
        listGroup.append(listItem);
    });
    $('#store-file-list').html(listGroup);
}

/**
 * Retrieves and logs the names of all selected files in the jsTree to the console.
 */
function processSelectedFiles() {
    let selectedFiles = $('#fileTree').jstree('get_selected', true);  // Retrieve selected nodes with full data
    let selectedFileNames = selectedFiles.map(file => file.text);  // Extract the file names
    console.log('Selected files for processing:', selectedFileNames);
}


/**
 * Toggles the visibility of the Stores and Store Details sections.
 * Adds click handlers to the headers to show/hide the respective sections.
 */
/**
 * Toggles the visibility of the Stores and Store Details sections.
 * Adds click handlers to the headers to show/hide the respective sections.
 */
document.addEventListener('DOMContentLoaded', function () {
    const storesHeader = document.getElementById('storesHeader');
    const storeDetailsHeader = document.getElementById('storeDetailsHeader');
    const storesSection = document.getElementById('storesSection');
    const storeDetailsSection = document.getElementById('storeDetailsSection');

    storesHeader.addEventListener('click', function () {
        storesSection.style.display = storesSection.style.display === 'none' ? 'block' : 'none';
    });

    storeDetailsHeader.addEventListener('click', function () {
        storeDetailsSection.style.display = storeDetailsSection.style.display === 'none' ? 'block' : 'none';
    });
});

/**
 * Fetches the list of files from the server for a specified directory.
 * @param {string} directory - The directory to list files from.
 */
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

/**
 * Hides the store details section and associated elements.
 * (Currently not called, but may be useful for resetting UI state.)
 */
function resetStoreSelection() {
    $('#removeSelectedFilesBtn').hide();
    $('#vectorStoreContent').hide();
}

/**
 * Initializes jsTree for Vector Store Content and handles the removal of selected files.
 */
$(document).ready(function () {
    $('#removeSelectedFilesBtn').on('click', function () {
        let selectedFiles = $('#fileTree').jstree('get_selected');

        if (selectedFiles.length === 0) {
            alert('No files selected for removal.');
            return;
        }

        $.ajax({
            url: '/remove-vector-store-files',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({files: selectedFiles}),
            success: function (response) {
                if (response.success) {
                    alert('Selected files removed successfully.');
                    $('#fileTree').jstree('refresh');
                } else {
                    alert('Error removing files.');
                }
            },
            error: function () {
                alert('An error occurred while trying to remove files.');
            }
        });
    });
    $('#processSelectedFilesBtn').on('click', processSelectedFiles);
});

