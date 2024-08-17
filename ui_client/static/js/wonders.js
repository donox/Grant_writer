// wonders.js

function getList(listType) {
    const config = window.listConfigs[listType];
    if (typeof listConfigs === 'undefined') {                   // remove when loading is working
        console.error('listConfigs is not defined');            //
        return;                                                 //
    }                                                           //
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
            }

            const selectorElement = $(`#${config.selectorId}`);
            if (selectorElement.length > 0) {
                populateSelector(selectorElement, data);
            }
        })
        .catch(error => console.error(`Fetch Error for ${listType}:`, error));
}

function populateTable(tableElement, data, config) {
    const tbody = tableElement.find('tbody');
    tbody.empty();

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
        tbody.append(row);
    });

    // Add "New Item" row
    const newItemRow = $('<tr>').addClass('new-item-row');
    const newItemCell = $('<td>')
        .attr('colspan', config.columns.length + 1)
        .text(config.newItemText)
        .on('click', () => openAssistantPopup(
            data.map(item => item.name),
            addAssistant
        ));
    newItemRow.append(newItemCell);
    tbody.append(newItemRow);
}

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

// Generic utility functions can go here

// Export functions if using modules
// export { getList, populateTable, populateSelector };