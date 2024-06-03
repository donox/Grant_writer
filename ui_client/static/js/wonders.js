//function to use AJAX to get a list of existing threads (conversations) the user may choose from
function get_list_of_threads() {
    let user = 'don';
    $.ajax({
        url: '/get-thread-list/' + user,
        type: 'GET',
        dataType: 'json',
        success: function (data) {
            // Find the table body
            let tbodyObj = $('#threads');
            // alert("updating threads");

            // Clear existing rows (if any)
            tbodyObj.empty();

            // Loop through the data and append rows
            data.forEach(function (thread) {
                let row = $('<tr></tr>');
                let nameCell = $('<td></td>').text(thread.name).addClass('clickable');
                nameCell.on('click', function () {
                    // You can perform other actions here
                    let prohibitedNames = ['NEW CONVERSATION', 'main'];
                    if (thread.name.trim() == 'NEW CONVERSATION') {
                        openPopup(prohibitedNames, function (result) {
                            // alert("ADD THREAD " + result.name);
                            addThread(result, user);
                        })
                    } else {
                        // alert("USE THREAD" + thread.name);
                        switchToQuery(thread.name, user);
                    }
                });
                let purposeCell = $('<td></td>').text(thread.purpose);
                row.append(nameCell, purposeCell);
                tbodyObj.append(row);
            });
            $('#threads').append(tbodyObj.outerHTML)

        },
        error: function (xhr, status, error) {
            console.error("Error fetching thread list:", error);
        }
    });
}
//Update screen with current thread list
get_list_of_threads();

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

//Swtich user page to query_processor
function switchToQuery(name, user) {
    $.ajax({
        url: '/switch-to-query/' + user,
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify({name: name}),
        success: function (response) {
            // alert("Now using thread:" + response.name);
            if (response.redirectUrl) {
                window.location.href = response.redirectUrl;
                $('#threaduser').val(response.user);
                $('#threadname').val(response.thread_name);
                $('#threadassistant').val(response.assistant);
            }
        },
        error: function (xhr, status, error) {
            console.error("Error adding thread:", error);
        },
    });
}


// Function to accept a name and purpose for a new thread to be created
function openPopup(prohibitedNames, callback) {
    // Convert prohibited names to lowercase for case-insensitive comparison
    let lowerCaseProhibitedNames = prohibitedNames.map(name => name.toLowerCase());

    $('#popupOverlay, #popupForm').show();

    $('#closeBtn').click(function () {
        $('#popupOverlay, #popupForm').hide();
    });

    $('#submitBtn').click(function () {
        let name = $('#nameInput').val().trim();
        let purpose = $('#purposeInput').val().trim();

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

        $('#popupOverlay, #popupForm').hide();
        callback(result);
    });
}
