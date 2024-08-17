// wonders_assistants.js

function get_list_of_assistants() {
    fetch('/get-assistant-list/', {
        method: 'GET',
        headers: {
            'datatype': 'json',
        },
    })
        .then(response => response.json())
        .then(data => {
            let tbodyObj = $('#assistants tbody');
            tbodyObj.empty();

            data.forEach(function (assistant) {
                let row = $('<tr class="assistantRow"></tr>');
                let nameCell = $('<td class="assistantName"></td>').text(assistant.name).addClass('clickable');
                let idCell = $('<td class="assistantID"></td>').text(assistant.id);
                let deleteButton = $('<button type="button" class="deleteAssistant btn btn-sm btn-danger">Delete</button>')
                let actionsCell = $('<td></td>').append(deleteButton);
                row.append(nameCell, idCell, actionsCell);
                tbodyObj.append(row);
            });

            // Add 'NEW ASSISTANT' option only once, at the end of the table
            let newAssistantRow = $('<tr class="assistantRow newAssistantRow"></tr>');
            let newAssistantCell = $('<td colspan="3" class="assistantName clickable text-center"><strong>NEW ASSISTANT</strong></td>');
            newAssistantRow.append(newAssistantCell);
            tbodyObj.append(newAssistantRow);

            // Add click event for assistant names
            $('.assistantName').on('click', function () {
                if ($(this).closest('.newAssistantRow').length) {
                    openAssistantPopup(['NEW ASSISTANT'], function (result) {
                        addAssistant(result);
                    });
                } else {
                    let assistantId = $(this).siblings('.assistantID').text();
                    loadAssistantDetails(assistantId);

                    // Highlight the selected assistant
                    $('.assistantRow').removeClass('selected');
                    $(this).closest('.assistantRow').addClass('selected');

                    // Scroll to assistant details on mobile
                    if (window.innerWidth <= 768) {
                        $('html, body').animate({
                            scrollTop: $("#assistantDetails").offset().top
                        }, 500);
                    }
                }
            });
        })
        .catch(error => console.error('Fetch Error: ' + error));
}

function loadAssistantDetails(assistantId, isNew) {
    fetch(`/get-assistant-details/${assistantId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            displayAssistantDetails(data);
        })
        .catch(error => console.error('Error loading assistant details:', error));
}

function displayAssistantDetails(assistant) {
    $('#assistantDetails').show();
    $('#assistantName').val(assistant.name);
    $('#assistantId').val(assistant.id);
    $('#assistantInstructions').val(assistant.instructions);

    // Add more fields as necessary
}

function clearAssistantDetails() {
    $('#assistantName').text('');
    $('#assistantId').text('');
    $('#assistantInstructions').val('');
    // Clear more fields as necessary

    // Hide the assistant details section
    $('#assistantDetails').hide();
}

function updateAssistantDetails() {
    let assistantId = $('#assistantId').val();
    let updatedData = {
        name: $('#assistantName').val(),
        instructions: $('#assistantInstructions').val(),
        // Add more fields as necessary
    };

    fetch(`/update-assistant/${assistantId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Assistant updated successfully');
                get_list_of_assistants(); // Refresh the list
            } else {
                alert('Failed to update assistant: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error updating assistant:', error);
            alert('An error occurred while updating the assistant');
        });
}

function deleteAssistant(assistantId) {
    if (confirm('Are you sure you want to delete this assistant?')) {
        fetch(`/delete-assistant/${assistantId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Assistant deleted successfully');
                    get_list_of_assistants(); // Refresh the list
                } else {
                    alert('Failed to delete assistant: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error deleting assistant:', error);
                alert('An error occurred while deleting the assistant');
            });
    }
}


function openAssistantPopup(prohibitedNames, callback) {
// Show the popup
    $('#popupAssistantOverlay, #popupAssistantForm').show();

    // Clear any previous input
    $('#assistantNameInput').val('');

    // Handle form submission
    $('#assistantSubmitBtn').off('click').on('click', function () {
        let name = $('#assistantNameInput').val().trim();

        if (prohibitedNames.includes(name)) {
            alert('This name is not allowed. Please choose a different name.');
            return;
        }

        if (name) {
            // Hide the popup
            $('#popupAssistantOverlay, #popupAssistantForm').hide();

            // Call the callback with the new assistant data
            callback({name: name});
        } else {
            alert('Please enter a name for the new assistant.');
        }
    });

    // Handle popup close
    $('#assistantCloseBtn').off('click').on('click', function () {
        $('#popupAssistantOverlay, #popupAssistantForm').hide();
    });
}

function addAssistant(assistantData) {
    fetch('/add-new-assistant/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(assistantData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('New assistant added successfully');
                get_list_of_assistants(); // Refresh the list
            } else {
                alert('Failed to add new assistant');
            }
        })
        .catch(error => console.error('Error adding new assistant:', error));
}

// Export functions if using modules
// export {
//     loadAssistantDetails,
//     displayAssistantDetails,
//     updateAssistantDetails,
//     deleteAssistant,
//     openAssistantPopup,
//     addAssistant
// };