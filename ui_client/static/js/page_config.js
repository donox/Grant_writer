
// wonders_page_config.js

window.pageConfigs = {
    assistantProcessorPage: {
        lists: ['assistants'],
        eventListeners: [
            { selector: '#updateAssistant', event: 'click', handler: 'updateAssistantDetails' }
        ]
    },
    indexPage: {
        lists: ['assistants', 'threads', 'stores'],
        eventListeners: []
    }
    // Add configurations for other pages as needed
};

// Export if using modules
// export default pageConfigs;