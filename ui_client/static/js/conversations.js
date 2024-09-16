// conversations.js

$(document).ready(function () {
    console.log("Document ready, initializing conversation functionality...");

    // Handle the click on the "Select a Conversation" button
    $('#selectConversationBtn').on('click', function () {
        console.log("Select Conversation button clicked");
        $('#popupOverlay').fadeIn();
        fetchAvailableConversations();
    });

    // Function to fetch available conversations
    function fetchAvailableConversations() {
        console.log("Fetching available conversations");
        $.ajax({
            url: '/get-conversations',
            method: 'GET',
            success: function (response) {
                console.log("Received conversations:", response);
                const $dropdown = $('#conversationSelect');
                $dropdown.empty();
                $dropdown.append('<option value="">Please select a conversation</option>');

                response.forEach(function (convo) {
                    $dropdown.append(`<option value="${convo.id}">${convo.name}</option>`);
                });
            },
            error: function (err) {
                console.error("Failed to load available conversations:", err);
            }
        });
    }

    // Handle the form submission (selecting a conversation)
    $('#selectConversationSubmitBtn').on('click', function () {
        const selectedConvoId = $('#conversationSelect option:selected').val();
        const selectedConvoName = $('#conversationSelect option:selected').text();

        if (selectedConvoId) {
            console.log("Selected conversation:", selectedConvoName, "with ID:", selectedConvoId);
            $('#selectedConversationHeader').text(selectedConvoName).show();
            $('#popupOverlay').fadeOut();

            loadConversationTree(selectedConvoId);
        } else {
            console.log("No conversation selected");
            alert('Please select a conversation.');
        }
    });

    function loadConversationTree(conversationId) {
        console.log("Loading conversation tree for ID:", conversationId);
        $.ajax({
            url: `/get-conversation-tree/${conversationId}`,
            method: 'GET',
            success: function (response) {
                console.log("Received tree data:", response);
                $('#conversationTree').jstree("destroy").empty();
                $('#conversationTree').jstree({
                    'core': {
                        'data': response.map(node => ({
                            id: node.id,
                            text: `<i class='fa fa-cog clickable-cog'></i> ${node.text}`,  // Multiple icons for parent node
                            icon: false,  // Disable default jsTree icons, as we are adding our own
                            state: node.state || {opened: false},  // Use the state from response or default
                            datums: node.datums,
                            children: node.children ? node.children.map(child => ({
                                id: child.id,
                                text: `<i class='fa fa-cog clickable-cog'></i> ${child.text}`,  // Icons for child node
                                icon: false,
                                state: child.state || {opened: false},
                                datums: child.datums,
                                children: child.children || []  // Recursively handle child nodes if any
                            })) : []  // Handle children if they exist
                        })),
                        'check_callback': true,
                        'themes': {
                            'name': 'default',
                            'icons': true
                        }
                    },
                    'types': {
                        'default': {
                            'icon': 'fa fa-folder'
                        },
                        'file': {
                            'icon': 'fa fa-file'
                        }
                    },
                    'plugins': [],
                }).on('ready.jstree', function () {
                    renderAllNodes();
                    cogClicker();
                }).on('open_node.jstree close_node.jstree', function (e, data) {
                    console.log(`Node ${data.node.id} ${e.type === 'open_node' ? 'opened' : 'closed'}`);
                    console.log("Node state:", data.node.state);
                    console.log("DOM state:", $('#' + data.node.id).hasClass('jstree-open'));
                })
            },
            error: function (err) {
                console.error("Failed to load the conversation tree:", err);
            }
        });
    }

// Event listener for clicking on the fa-cog icon
    function cogClicker() {
        $(document).on('click', '.clickable-cog', function (e) {
            e.stopPropagation();  // Prevent event from bubbling up to the node click event
            e.preventDefault();   // Prevent the default jsTree behavior

            // Find the closest `li` element (which represents the node in jsTree)
            let $nodeElement = $(this).closest('li');

            // Get the node's ID
            let nodeId = $nodeElement.attr('id');

            // Use jsTree's API to get the actual node object
            let tree = $('#conversationTree').jstree(true);  // Get the jsTree instance
            let node = tree.get_node(nodeId);  // Get the node object by its ID
            renderNodeContent(node);


            // Now you have the node object and can do whatever you need
            // console.log('COG Clicked - Node ID:', nodeId);
            // console.log('Node object:', node);

        });
    }


    function renderAllNodes() {
        // console.log("Rendering all nodes");
        // $('#conversationTree').find('.jstree-node').each(function () {
        //     let nodeId = $(this).attr('id');
        //     let node = $('#conversationTree').jstree(true).get_node(nodeId);
        //     renderNodeContent(node);
        // });
    }

    function renderNodeContent(node) {
        console.log("Rendering content for node:", node.id);
        const nodeId = node.id;
        const nodeData = node.original.datums;

        const nodeContent = $('<div>').addClass('node-content');
        const nodeAttributes = $('<div>').addClass('node-attributes')
        // .append($('<span>').addClass('node-name').text(nodeData.name))
        .append($('<span>').addClass('node-date').text(' ' + nodeData.datetime))
        // .append($('<span>').addClass('node-status').text(' ' + nodeData.status));

        const nodeActions = $('<div>').addClass('node-actions')
            .append($('<button>').addClass('btn btn-primary btn-sm btn-save').text('Save'))
            .append($('<button>').addClass('btn btn-secondary btn-sm btn-copy').text('Copy'))
            .append($('<button>').addClass('btn btn-danger btn-sm btn-delete').text('Delete'))
            .append($('<button>').addClass('btn btn-secondary btn-sm btn-close').text('Close'));


        const nodeEditor = $('<div>').addClass('node-editor')
            .attr('contenteditable', 'true')
            .text(nodeData.content);

        nodeContent.append(nodeAttributes, nodeActions, nodeEditor);

        // Append the node content after the jstree-anchor, not inside it
        $("#elementDisplay").append(nodeContent);
        // Attach other event handlers
        attachNodeEventHandlers(nodeId);
    }

    function attachNodeEventHandlers(nodeId) {
        // Attach event handlers for save, copy, delete buttons
        $(`#${nodeId} .btn-save`).on('click', function (e) {
            e.stopPropagation();
            saveNodeContent(nodeId);
        });

        $(`#${nodeId} .btn-copy`).on('click', function (e) {
            e.stopPropagation();
            copyToClipboard($(`#${nodeId} .node-editor`).text());
        });

        $(`#${nodeId} .btn-delete`).on('click', function (e) {
            e.stopPropagation();
            deleteNode(nodeId);
        });

         $(".node-content .btn-close").on('click', function (e) {
            e.stopPropagation();
            $(this).closest('.node-content').remove();
        });

        // Prevent propagation when clicking on node content
        $(`#${nodeId} > .node-content`).on('click', function (e) {
            e.stopPropagation();
        });

    }

    function saveNodeContent(nodeId) {
        const content = $(`#${nodeId} .node-editor`).text();
        console.log("Saving content for node:", nodeId, "Content:", content);
        // Make an AJAX call to save the content
        // Implement the actual save functionality here
    }

    function copyToClipboard(content) {
        console.log("Copying to clipboard:", content);
        navigator.clipboard.writeText(content).then(function () {
            console.log("Content copied to clipboard");
            alert('Content copied to clipboard!');
        }, function (err) {
            console.error('Could not copy text: ', err);
        });
    }

    function deleteNode(nodeId) {
        console.log("Attempting to delete node:", nodeId);
        if (confirm('Are you sure you want to delete this node?')) {
            console.log("Deletion confirmed for node:", nodeId);
            $('#conversationTree').jstree(true).delete_node(nodeId);
            // Optionally make an AJAX call to delete the node on the server
            // Implement the actual delete functionality here
        }
    }

    // Handle closing the popup without submitting
    $('#closePopupBtn').on('click', function () {
        console.log("Close popup button clicked");
        $('#popupOverlay').fadeOut();
    });

    // Example of how to get checked nodes (can be used when needed)
    function getCheckedNodes() {
        let checkedNodes = $('#conversationTree').jstree('get_checked', true);
        console.log("Checked Nodes:", checkedNodes);
        return checkedNodes;
    }

    $('#conversationTree').on('open_node.jstree close_node.jstree', function (e, data) {
        console.log("OPEN CLOSE NODE: " + data.node.id + " FUNC: " + e.type)
        const nodeId = data.node.id;
        if (e.type === 'close_node') {
            $(`#${nodeId} > .node-content`).hide();
        } else {
            $(`#${nodeId} > .node-content`).show();
        }
    });

    /* TEMP DEBUGGING */
    $('#conversationTree').on('open_node.jstree close_node.jstree', function (e, data) {
        console.log(`Node ${data.node.id} ${e.type === 'open_node' ? 'opened' : 'closed'}`);
        console.log("Node state:", data.node.state);
        console.log("DOM state:", $('#' + data.node.id).hasClass('jstree-open'));
    });

    console.log("Conversation functionality initialized");
});