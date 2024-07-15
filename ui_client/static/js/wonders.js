//function to use AJAX to get a list of existing threads (conversations) the user may choose from
function get_list_of_threads() {
    let user = 'don';
    let tbodyObj = $('#threads');     // Find table body
    let currentAssistant = $('#chooseRunAssistant');
    fetch('/get-thread-list/' + user, {
        method: 'GET',
        dataType: 'json',
    })
        .then(response => response.json())
        .then(data => {
                let alreadyDone = [];   // Hack to prevent multiple copies (till problem found)
                let tbodyObj = $('#threads');
                // Clear existing rows (if any)
                tbodyObj.empty();


                // Loop through the data and append rows,
                // for each row display a name with link to query_processor on that thread,
                // display a delete button that will delete the thread.
                data.forEach(function (thread) {
                        if (!alreadyDone.includes(thread.name)) {
                            let row = $('<tr class="threadRow"></tr>');
                            let nameCell = $('<td class="threadName "></td>').text(thread.name).addClass('clickable');
                            nameCell.on('click', function () {
                                // You can perform other actions here
                                let prohibitedNames = ['NEW CONVERSATION', 'main'];
                                if (thread.name.trim() == 'NEW CONVERSATION') {
                                    openThreadPopup(prohibitedNames, function (result) {
                                        // result is dict of name/purpose
                                        addThread(result, user);
                                    })
                                } else if (typeof ($(currentAssistant).text()) == 'undefined') {
                                    alert("There is no selected assistant")
                                } else {
                                    let asst = $(currentAssistant).find('.assistantID').text();
                                    switchToQuery(thread.name, asst, user);
                                }
                            });
                            let purposeCell = $('<td class="marker isSelectedThread"></td>').text(thread.purpose);
                            let deleteButton = $('<button type="button" class="deleteThread btn btn-primary">Delete</button>')
                            row.append(nameCell, purposeCell, deleteButton);
                            tbodyObj.append(row);
                        }
                    }
                )
                $('#threads').append(tbodyObj.outerHTML)
                // location.href = location.href;    //cause page to reload
                $('.deleteThread').on('click', function () {
                    const threadText = $(this).closest('.threadRow').find('.threadName').text();
                    let data = {text: threadText}

                    fetch('/delete-thread', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    })
                        .then(response => response.json())
                        .then(data => {
                                get_list_of_threads();
                            }
                        )
                        .catch(error => console.error('Fetch Error(delete-thread): ' + error))
                })
                $('.isSelectedThread').each(function () {
                    $(this).addClass('clickable');
                    $(this).on('click', function () {
                        $('#threads .marker').removeClass('isSelectedThread').removeClass('bg-info');
                        $(this).addClass('isSelectedThread').addClass('bg-info');
                        let thread = $('#chooseRunThread')
                        $(thread).find('.threadID').text($(this).parent().find('.threadID').text())
                        $(thread).find('.threadName').text($(this).parent().find('.threadName').text())
                    });
                });
            }
        )
        .catch(error => console.log('Fetch Error(/get-thread-list): ' + error))
}

function get_list_of_assistants() {
    let user = 'don';                   // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    fetch('/get-assistant-list/', {
        method: 'GET',
        headers: {
            'datatype': 'json',
        },
    })
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) {
                console.log('NOT DATA.' + data)
            }
             // Find the table body
        let tbodyObj = $('#assistants');

        // Clear existing rows (if any)
        tbodyObj.empty();
        // Loop through the data and append rows,
        // for each row display a name with link to assistant_processor.
        // display a delete button that will delete the assistant.
        data.forEach(function (assistant) {
            let row = $('<tr class="assistantRow"></tr>');
            let nameCell = $('<td class="assistantName"></td>').text(assistant.name).addClass('clickable');
            nameCell.on('click', function () {
                // You can perform other actions here
                let prohibitedNames = ['NEW ASSISTANT'];
                if (assistant.name.trim() == 'NEW ASSISTANT') {
                    openAssistantPopup(prohibitedNames, function (result) {
                        addAssistant(result);
                    })
                } else {
                    // alert("USE THREAD" + thread.name);
                    switchToAssistant(assistant.name, assistant.id);
                }
            });
            let idCell = $('<td class="assistantID isSelected"></td>').text(assistant.id);
            let deleteButton = $('<button type="button" class="deleteAssistant btn btn-primary">Delete</button>')
            row.append(nameCell, idCell, deleteButton);
            tbodyObj.append(row);
        });
        $('#assistants').append(tbodyObj.outerHTML)
        // location.href = location.href;    //cause page to reload
        $('.deleteAssistant').on('click', function () {
            const assistantText = $(this).closest('.assistantRow').find('.assistantID').text();

            $.ajax({
                url: 'delete-assistant',
                method: 'POST',
                data: {
                    text: assistantText
                },
                success: function (response) {
                    get_list_of_assistants();
                    console.log('Success', response);
                },
                error: function (error) {
                    console.log('Error', error);
                }
            })
        })
        $('.isSelected').each(function () {
            $(this).addClass('clickable');
            $(this).on('click', function () {
                $('#assistants .assistantID').removeClass('isSelected').removeClass('bg-info');
                $(this).addClass('isSelected').addClass('bg-info');
                let asst = $('#chooseRunAssistant')
                $(asst).find('.assistantID').text($(this).text())
                $(asst).find('.assistantName').text($(this).parent().find('.assistantName').text())
            });
        });



        })
        .catch(error => console.error('Fetch Error: ' + error))
}

//Update screen with current thread and assistant lists
get_list_of_threads();
get_list_of_assistants();

function addThread(jsonData, user) {
    $.ajax({
        url: '/add-new-thread/' + user,
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify((jsonData)),
        success: function (data) {
            // alert('Thread Added' + data)
            get_list_of_threads()
        },
        error: function (xhr, status, error) {
            console.error("Error adding thread:", error);
        },
    });

}

function addAssistant(jsonData) {
    $.ajax({
        url: '/add-new-assistant/',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify((jsonData)),
        success: function (data) {
            // alert('Assistant Added' + data)
            get_list_of_assistants()
        },
        error: function (xhr, status, error) {
            console.error("Error adding thread:", error);
        },
    });
}

//Swtich user page to query_processor
function switchToQuery(name, assistant, user) {
    let data = {
        name: name,
        user: user,
        assistant: assistant
    }
    fetch('/switch-to-query/', {
        method: 'POST',
        headers: {
            contentType: 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
                if (!Array.isArray(data)) {
                    console.log('NOT DATA.' + data)
                }
                url = data['redirectUrl'];
                window.location.href = url;
            }
        )
        .catch(error => console.error('Fetch Error: ' + error))
}

//Swtich user page to assistant manager page
function switchToAssistant(name, id) {
    let data = {name: name, id: id}
    fetch('/switch-to-assistant/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data)) {
                console.log('NOT DATA.' + data)
            }
            let params = {name: data['name'], assistant: data['assistant']}
            let queryString = Object.keys(params)
                .map(function (key) {
                    return encodeURIComponent(key) + '=' + encodeURIComponent(params[key]);
                })
                .join('&')
            window.location.href = data['redirectUrl'] + "?" + queryString;
        })
        .catch(error => console.error('Fetch Error: ' + error))

}


// Function to accept a name and purpose for a new thread to be created
function openThreadPopup(prohibitedNames, callback) {
    // Convert prohibited names to lowercase for case-insensitive comparison
    let lowerCaseProhibitedNames = prohibitedNames.map(name => name.toLowerCase());

    $('#popupThreadOverlay, #popupThreadForm').show();

    $('#threadCloseBtn').click(function () {
        $('#popupAThreadOverlay, #popupThreadForm').hide();
    });

    $('#threadSubmitBtn').click(function () {
        let name = $('#threadNameInput').val().trim();
        let purpose = $('#threadPurposeInput').val().trim();

        if (lowerCaseProhibitedNames.includes(name.toLowerCase())) {
            alert('This name is prohibited.');
            return;
        }

        let result = {
            name: name,
            purpose: purpose
        };
        // console.log(result);
        // alert('Submitted JSON: ' + JSON.stringify(result));

        $('#popupThreadOverlay, #popupThreadForm').hide();
        callback(result);
    });
}

// Function to accept a name and purpose for a new thread to be created
function openAssistantPopup(prohibitedNames, callback) {
    // Convert prohibited names to lowercase for case-insensitive comparison
    let lowerCaseProhibitedNames = prohibitedNames.map(name => name.toLowerCase());

    $('#popupAssistantOverlay, #popupAssistantForm').show();

    $('#assistantCloseBtn').click(function () {
        $('#popupAAssistantOverlay, #popupAssistantForm').hide();
    });

    $('#assistantSubmitBtn').click(function () {
        let name = $('#assistantNameInput').val().trim();

        if (lowerCaseProhibitedNames.includes(name.toLowerCase())) {
            alert('This name is prohibited.');
            return;
        }
        let result = {
            name: name,
        };
        // console.log(result);
        // alert('Submitted JSON: ' + JSON.stringify(result));

        $('#popupAssistantOverlay, #popupAssistantForm').hide();
        callback(result);
    });
}

// Function to resize textareas to fit content
function adjustHeight(textarea) {
    $(textarea).css('height', 'auto'); // Reset the height
    $(textarea).css('height', textarea.scrollHeight + 'px'); // Set the height to scrollHeight

}

function runQuery() {
    let user = 'Don';  // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    let thread = $('#chooseRunThread .threadName').text()
    let asst = $('#chooseRunAssistant .assistantID').text()
    switchToQuery(thread, asst, user)
}

