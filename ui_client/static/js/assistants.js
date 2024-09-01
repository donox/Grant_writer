// wonders_assistants.js

//

// function loadAssistantDetails(assistantId, isNew) {
//     fetch(`/get-assistant-details/${assistantId}`, {
//         method: 'GET',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//     })
//         .then(response => response.json())
//         .then(data => {
//             displayAssistantDetails(data);
//         })
//         .catch(error => console.error('Error loading assistant details:', error));
// }

function displayAssistantDetails(assistant) {
    $('#assistantDetails').show();
    const form = $('#assistantForm');
    form.empty();

    listConfigs.assistants.detailFields.forEach(field => {
        const fieldHtml = createFieldHtml(field, assistant[field.name]);
        form.append(fieldHtml);
    });
}

function createFieldHtml(field, value) {
    let inputHtml;
    if (field.type === 'textarea') {
        inputHtml = `<textarea id="${field.name}" name="${field.name}" class="form-control" ${field.required ? 'required' : ''} ${field.readonly ? 'readonly' : ''}>${value || ''}</textarea>`;
    } else if (field.type === 'select') {
        const options = field.options.map(option =>
            `<option value="${option}" ${option === value ? 'selected' : ''}>${option}</option>`
        ).join('');
        inputHtml = `<select id="${field.name}" name="${field.name}" class="form-control" ${field.required ? 'required' : ''} ${field.readonly ? 'readonly' : ''}>${options}</select>`;
    } else {
        inputHtml = `<input type="${field.type}" id="${field.name}" name="${field.name}" value="${value || ''}" class="form-control" ${field.required ? 'required' : ''} ${field.readonly ? 'readonly' : ''}>`;
    }

    return `
        <div class="form-group">
            <label for="${field.name}">${field.label}:</label>
            ${inputHtml}
        </div>
    `;
}

function updates() {
    const assistantId = $('#id').val();
    const updatedData = {};

    listConfigs.assistants.detailFields.forEach(field => {
        if (!field.readonly) {
            updatedData[field.name] = $(`#${field.name}`).val();
        }
    });

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
                getList('assistants'); // Refresh the list
            } else {
                alert('Failed to update assistant: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error updating assistant:', error);
            alert('An error occurred while updating the assistant');
        });
}


// function displayAssistantDetails(assistant) {
//     $('#assistantDetails').show();
//     $('#assistantName').val(assistant.name);
//     $('#assistantId').val(assistant.id);
//     $('#assistantInstructions').val(assistant.instructions);
//
//     // Add more fields as necessary
// }

function clearAssistantDetails() {
    $('#assistantName').text('');
    $('#assistantId').text('');
    $('#assistantInstructions').val('');
    // Clear more fields as necessary

    // Hide the assistant details section
    $('#assistantDetails').hide();
}

// function updateAssistantDetails() {
//     let assistantId = $('#assistantId').val();
//     let updatedData = {
//         name: $('#assistantName').val(),
//         instructions: $('#assistantInstructions').val(),
//         // Add more fields as necessary
//     };
//
//     fetch(`/update-assistant/${assistantId}`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(updatedData)
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert('Assistant updated successfully');
//                getList('assistants'); // Refresh the list
//             } else {
//                 alert('Failed to update assistant: ' + (data.message || 'Unknown error'));
//             }
//         })
//         .catch(error => {
//             console.error('Error updating assistant:', error);
//             alert('An error occurred while updating the assistant');
//         });
// }

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
                    getList('assistants');
                    ; // Refresh the list
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

// function addAssistant(assistantData) {
//     fetch('/add-new-assistant/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(assistantData)
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert('New assistant added successfully');
//                 getList('assistants'); // Refresh the list
//             } else {
//                 alert('Failed to add new assistant');
//             }
//         })
//         .catch(error => console.error('Error adding new assistant:', error));
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

$(document).ready(function () {
    $('#updateAssistant').on('click', updateAssistantDetails);
});