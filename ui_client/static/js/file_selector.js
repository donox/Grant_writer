

    function updateFileBrowser(directory) {
        fetch('/get_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({directory: directory}),
        })
            .then(response => response.json())
            .then(data => {
                currentDirectory = data.current_directory;
                $('#current-directory').text('Current directory: ' + currentDirectory);

                let fileList = $('#file-list');
                fileList.empty();

                if (currentDirectory !== '/') {
                    fileList.append('<li><a href="#" class="directory" data-path="' +
                        data.current_directory + '/..">..</a></li>');
                }

                data.directories.forEach(function (dir) {
                    fileList.append('<li><a href="#" class="directory" data-path="' +
                        data.current_directory + '/' + dir + '">' + dir + '</a></li>');
                });

                data.files.forEach(function (file) {
                    fileList.append('<li><a href="#" class="file" data-path="' +
                        data.current_directory + '/' + file + '">' + file + '</a></li>');
                });
            })
            .catch(error => console.error('Error:', error));
    }

    // code to go in page using FileBrowser
    // $('#open-file-browser').click(function () {
    //     $('#file-browser').show();
    //     updateFileBrowser(currentDirectory);
    // });
    //
    // $('#close-file-browser').click(function () {
    //     $('#file-browser').hide();
    // });
    //
    // $('#file-list').on('click', '.directory', function (e) {
    //     e.preventDefault();
    //     updateFileBrowser($(this).data('path'));
    // });
    //
    // $('#file-list').on('click', '.file', function (e) {
    //     e.preventDefault();
    //     alert('Selected file: ' + $(this).data('path'));
    //     $('#file-browser').hide();
    // });

