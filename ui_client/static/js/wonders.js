// wonders.js

/**
 * Fetches and displays a list based on the specified list type configuration.
 * @param {string} listType - The type of list to fetch, based on configurations in listConfigs.
 */
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

/**
 * Populates a table with data based on configuration.
 * @param {jQuery} tableElement - The table DOM element to populate.
 * @param {Array} data - The data to display in the table.
 * @param {Object} config - The configuration object specifying columns and actions.
 */
function populateTable(tableElement, data, config) {
    const $tbody = tableElement.find('tbody');
    $tbody.empty();

    // Create and populate table header
    const $thead = tableElement.find('thead');
    $thead.empty();
    const headerRow = $('<tr>');
    config.columns.forEach(column => {
        const field = config.fields.find(f => f.name === column);
        headerRow.append($('<th>').text(field ? field.label : column));
    });
    headerRow.append($('<th>').text('Actions'));
    $thead.append(headerRow);

    // Populate table rows with data
    data.forEach(item => {
        const row = $('<tr>');
        config.columns.forEach(column => {
            row.append($('<td>').text(item[column]));
        });

        // Add action buttons for each row
        const actionCell = $('<td>');
        const viewEditBtn = $('<button>')
            .addClass('btn btn-sm btn-primary mr-2')
            .text('View/Edit')
            .on('click', () => config.onItemClick(item.id));
        actionCell.append(viewEditBtn);

        const deleteBtn = $('<button>')
            .addClass('btn btn-sm btn-danger')
            .text('Delete')
            .on('click', () => config.onDeleteClick(item.id));
        actionCell.append(deleteBtn);

        row.append(actionCell);
        $tbody.append(row);
    });

    // New item row for adding items
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

/**
 * Generates HTML for a form field based on configuration.
 * @param {Object} field - The configuration for the field.
 * @param {*} value - The current value for the field, if any.
 * @returns {string} The HTML string for the form field.
 */
function createFieldHtml(field, value) {
    let inputHtml;
    if (field.type === 'textarea') {
        inputHtml = `<textarea id="${field.name}" name="${field.name}" class="form-control" ${field.required ? 'required' : ''} ${field.readonly ? 'readonly' : ''}>${value || ''}</textarea>`;
    } else if (field.type === 'select') {
        const options = field.options.map(option =>
            `<option value="${option}" ${option === value ? 'selected' : ''}>${option}</option>`
        ).join('');
        inputHtml = `<select id="${field.name}" name="${field.name}" class="form-control" ${field.required ? 'required' : ''} ${field.readonly ? 'readonly' : ''}>${options}</select>`;
    } else if (field.type === 'filelist') {
        // Filelist type handling, assuming value is an array
        const items = value.map((item, index) => `
            <li class="list-group-item">
                <div class="form-check">
                    <input class="form-check-input" type="${field.selectionType || 'checkbox'}" name="${field.name}" value="${item}" id="${field.name}-${index}" ${field.readonly ? 'disabled' : ''}>
                    <label class="form-check-label" for="${field.name}-${index}">${item}</label>
                </div>
            </li>
        `).join('');
        inputHtml = `<ul class="list-group">${items}</ul>`;
    } else {
        inputHtml = `<input type="${field.type}" id="${field.name}" name="${field.name}" value="${value || ''}" class="form-control" ${field.required ? 'required' : ''} ${field.readonly ? 'readonly' : ''}>`;
    }

    return `<div class="form-group"><label for="${field.name}">${field.label}:</label>${inputHtml}</div>`;
}

/**
 * Populates a selector with options from the given data.
 * @param {jQuery} selectorElement - The selector DOM element to populate.
 * @param {Array} data - The data to populate into the selector.
 */
function populateSelector(selectorElement, data) {
    selectorElement.empty();
    selectorElement.append($('<option>', { value: '', text: '-- Select an item --' }));
    data.forEach(item => {
        selectorElement.append($('<option>', { value: item.id, text: item.name }));
    });
    selectorElement.trigger('change');
}

/**
 * Loads details for a specific item and displays them.
 * @param {string} itemType - The type of item to load.
 * @param {string} itemId - The ID of the item to load.
 */
function loadItemDetails(itemType, itemId) {
    const config = window.listConfigs[itemType];
    if (!config) {
        console.error(`No configuration found for item type: ${itemType}`);
        return;
    }

    fetch(`${config.detailsUrl}/${itemId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
    })
        .then(response => response.json())
        .then(data => {
            config.displayDetails(data);
        })
        .catch(error => console.error(`Error loading ${itemType} details:`, error));
}

// TODO: Remove this function when clear there is no need - else make generic
/**
 * Updates details for a specific item (assumed to be an assistant).
 * This function is currently specific to "assistant" type; consider generalizing for other types.
 * @param {string} itemType - The type of item to update.
 */
// function updateItemDetails(itemType) {
//     // Note: itemId is hardcoded as 'assistantId', which limits reusability
//     const itemId = $('#assistantId').val();
//     const updatedData = {
//         name: $('#assistantName').val(),
//         instructions: $('#assistantInstructions').val(),
//     };
//
//     fetch(`/update-assistant/${itemId}`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(updatedData)
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert('Assistant updated successfully');
//                 getList('assistants'); // Consider making 'assistants' dynamic
//             } else {
//                 alert(`Failed to update assistant: ${data.message || 'Unknown error'}`);
//             }
//         })
//         .catch(error => {
//             console.error('Error updating assistant:', error);
//             alert('An error occurred while updating the assistant');
//         });
// }

/**
 * Opens a popup form for creating a new item of the given list type.
 * @param {string} listType - The type of list for which the popup is opened.
 * @param {Array} existingNames - Array of existing names to check for duplicates.
 * @param {function} createCallback - Callback to execute on successful form submission.
 */
function openPopup(listType, existingNames, createCallback) {
    const config = window.listConfigs[listType];
    if (!config) {
        console.error(`No configuration found for list type: ${listType}`);
        return;
    }

    $('#popupOverlay, #popupForm').show();
    $('#popupTitle').text(`Create New ${listType.slice(0, -1)}`);

    const formContent = config.fields.map(field => createFieldHtml(field, '')).join('');
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
                return false;
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

/**
 * Sends a request to create a new item, then refreshes the list on success.
 * @param {string} listType - The type of list to which the item will be added.
 * @param {Object} itemData - The data for the new item to be created.
 */
function createNewItem(listType, itemData) {
    const config = window.listConfigs[listType];
    if (!config || !config.createUrl) {
        console.error(`Configuration or createUrl not found for ${listType}`);
        return;
    }

    fetch(config.createUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(itemData)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`New ${listType.slice(0, -1)} added successfully`);
                getList(listType);
            } else {
                alert(`Failed to add new ${listType.slice(0, -1)}: ${data.message || 'Unknown error'}`);
            }
        })
        .catch(error => console.error(`Error adding new ${listType.slice(0, -1)}:`, error));
}

$(document).ready(function() {
    // Initialization code goes here
    // Example: getList('stores'); or another specific list type on page load
});
