function loadThreadDetails(threadId, isNew) {
    fetch(`/get-thread-details/${threadId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            console.log("DETAILS" + data)
            displaythreadDetails(data);
        })
        .catch(error => console.error('Error loading thread details:', error));
}

// function displayThreadDetails(thread) {
//     $('#threadDetails').show();
//     const form = $('#threadForm');
//     form.empty();
//
//     listConfigs.threads.detailFields.forEach(field => {
//         const fieldHtml = createFieldHtml(field, thread[field.name]);
//         console.log("field: " + fieldHtml)
//         form.append(fieldHtml);
//     });
// }

function displayThreadDetails(thread) {
    console.log("Displaying thread details:", thread);
    $('#threadDetails').show();
    const form = $('#threadForm');
    console.log("Form element:", form);
    let formContent = '';
    listConfigs.threads.detailFields.forEach(field => {
        console.log("Processing field:", field);
        const fieldHtml = createFieldHtml(field, thread[field.name]);
        console.log("Created field HTML:", fieldHtml);
        formContent += fieldHtml;
    });
    form.html(formContent);
    console.log("Final form contents:", form.html());
}

//    
// function displayAssistantDetails(assistant) {
// 
// function clearAssistantDetails() {
//   
// function updateAssistantDetails() {
//    
function deleteThread(threadId) {
    if (confirm('Are you sure you want to delete this thread?')) {
        fetch(`/delete-thread/${threadId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('thread deleted successfully');
                    getList('threads') // Refresh the list x
                } else {
                    alert('Failed to delete thread: ' + (data.message || 'Unknown error'));
                }
            })
            .catch(error => {
                console.error('Error deleting thread:', error);
                alert('An error occurred while deleting the thread');
            });
    }
}

//
// function openAssistantPopup(prohibitedNames, callback) {
//
// function addAssistant(assistantData) {

// function addThread(threadData) {
//     fetch('/add-new-thread/', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(threadData)
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 alert('New thread added successfully');
//                 get_list('threads'); // Refresh the list
//             } else {
//                 alert('Failed to add new thread');
//             }
//         })
//         .catch(error => console.error('Error adding new thread:', error));
// }