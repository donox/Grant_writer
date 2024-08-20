// wonders.js

function getList(listType) {
    const config = window.listConfigs[listType];
    if (!config) {
        console.error(`No configuration found for list type: ${listType}`);
        return;
    }

    fetch(config.fetchUrl, {
        method: 'GET',
        headers: {'datatype': 'json'},
    })
        .then(response => response.json())
        .then(data => {
            const tableElement = $(`#${config.tableId}`);
            if (tableElement.length > 0) {
                populateTable(tableElement, data, config);
            } else {
                console.error(`Table element not found for ${listType}`);
            }

            const selectorElement = $(`#${config.selectorId}`);
            if (selectorElement.length > 0) {
                populateSelector(selectorElement, data);
            }
        })
        .catch(error => console.error(`Fetch Error for ${listType}:`, error));
}

// function populateTable(tableElement, data, config) {
//     const $tbody = tableElement.find('tbody');
//     $tbody.empty();
//
//     data.forEach(item => {
//         const row = $('<tr>');
//
//         config.columns.forEach(column => {
//             row.append($('<td>').text(item[column]));
//         });
//
//         // Add action buttons
//         const actionCell = $('<td>');
//
//         // View/Edit button
//         const viewEditBtn = $('<button>')
//             .addClass('btn btn-sm btn-primary mr-2')
//             .text('View/Edit')
//             .on('click', () => config.onItemClick(item.id));
//         actionCell.append(viewEditBtn);
//
//         // Delete button
//         const deleteBtn = $('<button>')
//             .addClass('btn btn-sm btn-danger')
//             .text('Delete')
//             .on('click', () => config.onDeleteClick(item.id));
//         actionCell.append(deleteBtn);
//
//         row.append(actionCell);
//         $tbody.append(row);
//     });
//
//     // Add "New Item" row
//     const newItemRow = $('<tr>').addClass('new-item-row');
//     const newItemCell = $('<td>')
//         .attr('colspan', config.columns.length + 1)
//         .text(config.newItemText)
//         .on('click', () => {
//             const existingNames = data.map(item => item.name);
//             openPopup(config.listType, existingNames, (newItemData) => createNewItem(config.listType, newItemData));
//         });
//     newItemRow.append(newItemCell);
//     $tbody.append(newItemRow);
// }
function populateTable(tableElement, data, config) {
    const $tbody = tableElement.find('tbody');
    $tbody.empty();

    // Create table header
    const $thead = tableElement.find('thead');
    $thead.empty();
    const headerRow = $('<tr>');
    config.columns.forEach(column => {
        const field = config.fields.find(f => f.name === column);
        headerRow.append($('<th>').text(field ? field.label : column));
    });
    headerRow.append($('<th>').text('Actions'));
    $thead.append(headerRow);

    // Populate table body
    data.forEach(item => {
        const row = $('<tr>');

        config.columns.forEach(column => {
            row.append($('<td>').text(item[column]));
        });

        // Add action buttons
        const actionCell = $('<td>');

        // View/Edit button
        const viewEditBtn = $('<button>')
            .addClass('btn btn-sm btn-primary mr-2')
            .text('View/Edit')
            .on('click', () => config.onItemClick(item.id));
        actionCell.append(viewEditBtn);

        // Delete button
        const deleteBtn = $('<button>')
            .addClass('btn btn-sm btn-danger')
            .text('Delete')
            .on('click', () => config.onDeleteClick(item.id));
        actionCell.append(deleteBtn);

        row.append(actionCell);
        $tbody.append(row);
    });

    // Add "New Item" row
    const newItemRow = $('<tr>').addClass('new-item-row');
    const newItemCell = $('<td>')
        .attr('colspan', config.columns.length + 1)
        .text(config.newItemText)
        .on('click', () => {
            const existingNames = data.map(item => item.name);
            openPopup(config.listType, existingNames, (newItemData) => createNewItem(config.listType, newItemData));
        });
    newItemRow.append(newItemCell);
    $tbody.append(newItemRow);
}
// function populateTable(tableElement, data, config) {
//     const tbody = tableElement.find('tbody');
//     tbody.empty();
//
//     data.forEach(item => {
//         const row = $('<tr>');
//
//         config.columns.forEach(column => {
//             row.append($('<td>').text(item[column]));
//         });
//
//         // Add action buttons
//         const actionCell = $('<td>');
//
//         // View/Edit button
//         const viewEditBtn = $('<button>')
//             .addClass('btn btn-sm btn-primary mr-2')
//             .text('View/Edit')
//             .on('click', () => config.onItemClick(item.id));
//         actionCell.append(viewEditBtn);
//
//         // Delete button
//         const deleteBtn = $('<button>')
//             .addClass('btn btn-sm btn-danger')
//             .text('Delete')
//             .on('click', () => config.onDeleteClick(item.id));
//         actionCell.append(deleteBtn);
//
//         row.append(actionCell);
//         tbody.append(row);
//     });
//
//     // Add "New Item" row
//     const newItemRow = $('<tr>').addClass('new-item-row');
//     const newItemCell = $('<td>')
//         .attr('colspan', config.columns.length + 1)
//         .text(config.newItemText)
//         .on('click', () => openAssistantPopup(
//             data.map(item => item.name),
//             addAssistant
//         ));
//     newItemRow.append(newItemCell);
//     tbody.append(newItemRow);
// }

function populateSelector(selectorElement, data) {
    selectorElement.empty();

    // Add a default option
    selectorElement.append($('<option>', {
        value: '',
        text: '-- Select an item --'
    }));

    // Add options for each item in the data
    data.forEach(item => {
        selectorElement.append($('<option>', {
            value: item.id,
            text: item.name
        }));
    });

    // Trigger change event to ensure any attached handlers are called
    selectorElement.trigger('change');
}

function loadItemDetails(itemType, itemId) {
    const config = window.listConfigs[itemType];
    if (!config) {
        console.error(`No configuration found for item type: ${itemType}`);
        return;
    }

    fetch(`${config.detailsUrl}/${itemId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            config.displayDetails(data);
        })
        .catch(error => console.error(`Error loading ${itemType} details:`, error));
}

function updateitemDetails(itemType) {
    let itemId = $('#assistantId').val();
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

// function openPopup(listType, existingNames, createCallback) {
//     const config = window.listConfigs[listType];
//     if (!config) {
//         console.error(`No configuration found for list type: ${listType}`);
//         return;
//     }
//
//     $('#popupOverlay, #popupForm').show();
//     $('#popupTitle').text(`Create New ${listType.slice(0, -1)}`);
//     $('#nameInput').val('');
//
//     $('#submitBtn').off('click').on('click', function() {
//         const name = $('#nameInput').val().trim();
//         if (name) {
//             if (existingNames.includes(name)) {
//                 alert(`A ${listType.slice(0, -1)} with this name already exists. Please choose a different name.`);
//             } else {
//                 createCallback({ name: name });
//                 $('#popupOverlay, #popupForm').hide();
//             }
//         } else {
//             alert('Please enter a name.');
//         }
//     });
//
//     $('#closeBtn').off('click').on('click', function() {
//         $('#popupOverlay, #popupForm').hide();
//     });
// }

// function openPopup(listType) {
//     console.log(`Opening popup for ${listType}`);
//     const config = window.listConfigs[listType];
//     if (!config) {
//         console.error(`No configuration found for list type: ${listType}`);
//         return;
//     }
//
//     // Get existing item names to check for duplicates
//     const existingNames = $(`#${config.tableId} tbody tr:not(.new-item-row) td:first-child`)
//         .map(function() { return $(this).text(); })
//         .get();
//
//     $('#popupOverlay, #popupForm').show();
//     $('#popupTitle').text(`Create New ${listType.slice(0, -1)}`);
//     $('#nameInput').val('');
//
//     $('#submitBtn').off('click').on('click', function() {
//         const name = $('#nameInput').val().trim();
//         if (name) {
//             if (existingNames.includes(name)) {
//                 alert(`A ${listType.slice(0, -1)} with this name already exists. Please choose a different name.`);
//             } else {
//                 createNewItem(listType, { name: name });
//                 $('#popupOverlay, #popupForm').hide();
//             }
//         } else {
//             alert('Please enter a name.');
//         }
//     });
//
//     $('#closeBtn').off('click').on('click', function() {
//         $('#popupOverlay, #popupForm').hide();
//     });
// }
// function createNewItem(listType, itemData) {
//     console.log(`Creating new ${listType} with data:`, itemData);
//     const config = window.listConfigs[listType];
//
//     fetch(config.createUrl, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(itemData)
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             alert(`New ${listType.slice(0, -1)} added successfully`);
//             getList(listType);  // Refresh the list
//         } else {
//             alert(`Failed to add new ${listType.slice(0, -1)}: ${data.message || 'Unknown error'}`);
//         }
//     })
//     .catch(error => console.error(`Error adding new ${listType.slice(0, -1)}:`, error));
// }

function openPopup(listType, existingNames, createCallback) {
    const config = window.listConfigs[listType];
    if (!config) {
        console.error(`No configuration found for list type: ${listType}`);
        return;
    }

    $('#popupOverlay, #popupForm').show();
    $('#popupTitle').text(`Create New ${listType.slice(0, -1)}`);

    const formContent = config.fields.map(field => {
        let inputElement;
        if (field.type === 'textarea') {
            inputElement = `<textarea id="${field.name}Input" class="form-control" ${field.required ? 'required' : ''}></textarea>`;
        } else if (field.type === 'select') {
            const options = field.options.map(option => `<option value="${option}">${option}</option>`).join('');
            inputElement = `<select id="${field.name}Input" class="form-control" ${field.required ? 'required' : ''}>${options}</select>`;
        } else {
            inputElement = `<input type="${field.type}" id="${field.name}Input" class="form-control" ${field.required ? 'required' : ''}>`;
        }
        return `
            <div class="form-group">
                <label for="${field.name}Input">${field.label}:</label>
                ${inputElement}
            </div>
        `;
    }).join('');

    $('#popupForm').html(`
        ${formContent}
        <button id="submitBtn" class="btn btn-primary">Create</button>
        <button id="closeBtn" class="btn btn-secondary">Cancel</button>
    `);

    $('#submitBtn').off('click').on('click', function() {
        const newItemData = {};
        let isValid = true;

        config.fields.forEach(field => {
            const value = $(`#${field.name}Input`).val().trim();
            if (field.required && !value) {
                alert(`${field.label} is required.`);
                isValid = false;
                return false;  // break the loop
            }
            newItemData[field.name] = value;
        });

        if (isValid) {
            if (existingNames.includes(newItemData.name)) {
                alert(`A ${listType.slice(0, -1)} with this name already exists. Please choose a different name.`);
            } else {
                createCallback(newItemData);
                $('#popupOverlay, #popupForm').hide();
            }
        }
    });

    $('#closeBtn').off('click').on('click', function() {
        $('#popupOverlay, #popupForm').hide();
    });
}

// function createNewItem(listType, itemData) {
//     const config = window.listConfigs[listType];
//     if (!config) {
//         console.error(`No configuration found for list type: ${listType}`);
//         return;
//     }
//
//     fetch(config.createUrl, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(itemData)
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             alert(`New ${listType.slice(0, -1)} added successfully`);
//             getList(listType);  // Refresh the list
//         } else {
//             alert(`Failed to add new ${listType.slice(0, -1)}: ${data.message || 'Unknown error'}`);
//         }
//     })
//     .catch(error => console.error(`Error adding new ${listType.slice(0, -1)}:`, error));
// }
// Set up event listeners for all list types
function createNewItem(listType, itemData) {
    const config = window.listConfigs[listType];
    if (!config || !config.createUrl) {
        console.error(`Configuration or createUrl not found for ${listType}`);
        return;
    }

    fetch(config.createUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(itemData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`New ${listType.slice(0, -1)} added successfully`);
            getList(listType); // Refresh the list
        } else {
            alert(`Failed to add new ${listType.slice(0, -1)}: ${data.message || 'Unknown error'}`);
        }
    })
    .catch(error => console.error(`Error adding new ${listType.slice(0, -1)}:`, error));
}
$(document).ready(function() {

});
// Generic utility functions can go here

// Export functions if using modules
// export { getList, populateTable, populateSelector };