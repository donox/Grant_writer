// wonders_config.js

var listConfigs;

function makeListConfigs() {
    listConfigs = {
        assistants: {
            listType: 'assistants',
            fetchUrl: '/get-assistants-list/',
            detailsUrl: '/get-assistant-details/',
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
            columns: ['name', 'id', 'description', 'model'],
            onItemClick: (id) => loadItemDetails('assistants', id),
            onDeleteClick: deleteAssistant,
            onNewItemClick: (existingNames) => openPopup('assistants', existingNames),
            displayDetails: displayAssistantDetails
        },
        threads: {
            listType: 'threads',
            fetchUrl: '/get-threads-list/',
            detailsUrl: '/get-thread-details/',
            createUrl: '/add-new-thread/',
            addItem: (data) => createNewItem('threads', data),
            tableId: 'threadsTable',
            selectorId: 'threadSelector',
            newItemText: 'CREATE NEW THREAD',
            fields: [
                {name: 'name', type: 'text', label: 'Name', required: true},
                {name: 'purpose', type: 'text', label: 'Purpose'},
            ],
            columns: ['name', 'id', 'purpose'],
            onItemClick: (id) => loadItemDetails('threads', id),
            onDeleteClick: deleteThread,
            onNewItemClick: (existingNames) => openPopup('threads', existingNames),
            // displayDetails: displayThreadDetails
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