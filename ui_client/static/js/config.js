// wonders_config.js

var listConfigs;

function makeListConfigs() {
    listConfigs = {
        assistants: {
            listType: 'assistants',
            fetchUrl: '/get-assistants-list/',
            detailsUrl: '/get-assistants-details/',
            updateUrl: '/update-assistant/', // URL for updating assistant details
            createUrl: '/add-new-assistant/',
            addItem: (data) => createNewItem('assistants', data),
            tableId: 'assistantsTable',
            selectorId: 'assistantSelector',
            newItemText: 'CREATE NEW ASSISTANT',
            fields: [                           // fields user must complete for new object
                {name: 'name', type: 'text', label: 'Name', required: true},
                {name: 'description', type: 'textarea', label: 'Description'},
                {name: 'model', type: 'select', label: 'Model', options: ['gpt-3.5-turbo', 'gpt-4']}
            ],
            detailFields: [            // fields that may be updated in the underlying object
                {name: 'name', type: 'text', label: 'Name', required: true},
                {name: 'id', type: 'text', label: 'ID', readonly: true},
                {name: 'instructions', type: 'textarea', label: 'Instructions'},
                {name: 'model', type: 'select', label: 'Model', options: ['gpt-3.5-turbo', 'gpt-4']},
                {name: 'description', type: 'textarea', label: 'Description'}
            ],
            columns: ['name', 'id', 'description', 'model'],  // fields shown in list of objects
            onItemClick: (id) => loadItemDetails('assistants', id),
            onDeleteClick: deleteAssistant,
            // onNewItemClick appears to be handled in wonders.js without referring to this config item.   !!!!!!!!!
            onNewItemClick: (existingNames) => openPopup('assistants', existingNames),
            displayDetails: displayAssistantDetails
        },
        threads: {
            listType: 'threads',
            fetchUrl: '/get-threads-list/',
            detailsUrl: '/get-threads-details/',
            createUrl: '/add-new-thread/',
            addItem: (data) => createNewItem('threads', data),
            tableId: 'threadsTable',
            selectorId: 'threadSelector',
            newItemText: 'CREATE NEW THREAD',
            fields: [
                {name: 'name', type: 'text', label: 'Name', required: true},
                {name: 'purpose', type: 'text', label: 'Purpose'},
            ],
            detailFields: [            // fields that may be updated in the underlying object
                {name: 'name', type: 'text', label: 'Name', required: true},
                {name: 'id', type: 'text', label: 'ID', readonly: true},
                {name: 'description', type: 'textarea', label: 'Description'}
            ],
            columns: ['name', 'id', 'purpose'],
            onItemClick: (id) => loadItemDetails('threads', id),
            onDeleteClick: deleteThread,
            onNewItemClick: (existingNames) => openPopup('threads', existingNames),
            displayDetails: displayThreadDetails
        },
        stores: {
            listType: 'stores',
            fetchUrl: '/get-stores-list/',
            detailsUrl: '/get-store-details/',
            createUrl: '/add-new-store/',
            addItem: (data) => createNewItem('stores', data),
            tableId: 'storesTable',
            selectorId: 'storeSelector',
            newItemText: 'NEW STORE',
            fields: [
                {name: 'name', type: 'text', label: 'Name', required: true},
                // {name: 'description', type: 'text', label: 'Description'},
            ],
            detailFields: [            // fields that may be updated in the underlying object
                {name: 'name', type: 'text', label: 'Name', required: true},
                {name: 'id', type: 'text', label: 'ID', readonly: true},
                {name: 'description', type: 'textarea', label: 'Description'},
                {name: 'files',  type: 'filelist', label: 'Vector Store Content',
                    required: false, readonly: false, selectionType: 'checkbox'}  // 'checkbox' for multiple selection, 'radio' for single selection
            ],
            columns: ['name', 'id', 'description'],
            onItemClick: (id) => loadItemDetails('stores', id),
            onDeleteClick: deleteStore,
            onNewItemClick: (existingNames) => openPopup('stores', existingNames),
            displayDetails: displayStoreDetails
        }
    }
}

// Export if using modules
// export default listConfigs;