// wonders_init.js

function initializePage() {

    // Check for the presence of specific div IDs to determine the page
    let pageConfig;
    makeListConfigs();
    if (document.getElementById('assistantManager')) {
        pageConfig = window.pageConfigs.assistantProcessorPage;
    } else if (document.getElementById('indexManager')) {  // Assuming you have a div with id 'indexManager' on the index page
        pageConfig = window.pageConfigs.indexPage;
    } else {
        console.error('No configuration found for this page');
        return;
    }

    if (!pageConfig) {
        console.error('No configuration found for this page');
        return;
    }

    pageConfig.lists.forEach(listType => {
        getList(listType);
    });

    pageConfig.eventListeners.forEach(listener => {
        const element = document.querySelector(listener.selector);
        if (element) {
            element.addEventListener(listener.event, window[listener.handler]);
        }
    });
}

// Call initializePage when the DOM is fully loaded
// document.addEventListener('load', initializePage);
document.addEventListener('DOMContentLoaded', initializePage);


// Export if using modules
// export { initializePage };