// wonders_page_config.js

window.pageConfigs = {
    assistantProcessorPage: {
        lists: ['assistants'],
        eventListeners: [
            {selector: '#updateAssistant', event: 'click', handler: 'updateAssistantDetails'}
        ]
    },
    indexPage: {
        // lists: ['assistants', 'threads', 'stores'],
        lists: ['assistants', 'threads'],
        eventListeners: []
    },
    threadPage: {
        lists: ['threads'],
        eventListeners: [
            {selector: '#updateThread', event: 'click', handler: 'updateThreadDetails'}
        ]
    },
    storePage: {
        lists: ['stores'],
        eventListeners: [
            {selector: '#updateStore', event: 'click', handler: 'updateStoreDetails'}
        ]
    },
        conversationPage: {
        lists: ['coversations'],
        eventListeners: [
            {selector: '#updateConversation', event: 'click', handler: 'updateConversationDetails'}
        ]
    },
    // Add configurations for other pages as needed
};

// Export if using modules
// export default pageConfigs;