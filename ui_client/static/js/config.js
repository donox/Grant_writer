// wonders_config.js

var listConfigs;
function makeListConfigs() {
    listConfigs = {
        assistants: {
            fetchUrl: '/get-assistant-list/',
            tableId: 'assistants',
            selectorId: 'assistantSelector',
            newItemText: 'NEW ASSISTANT',
            columns: ['name', 'id'],
            onItemClick: loadAssistantDetails,
            onDeleteClick: deleteAssistant
        },
        threads: {
            fetchUrl: '/get-thread-list/',
            tableId: 'threads',
            selectorId: 'threadSelector',
            newItemText: 'NEW THREAD',
            columns: ['name', 'id'],
            // onItemClick: loadThreadDetails,
            // onDeleteClick: deleteThread
        },
        stores: {
            fetchUrl: '/get-store-list/',
            tableId: 'stores',
            selectorId: 'storeSelector',
            newItemText: 'NEW STORE',
            columns: ['name', 'id'],
            // onItemClick: loadStoreDetails,
            // onDeleteClick: deleteStore
        }
    }
}

// Export if using modules
// export default listConfigs;