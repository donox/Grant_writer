// conversations.js

$(document).ready(function () {
    console.log("Document ready, initializing conversation functionality...");

    /**
     * Handles the click event for the "Select a Conversation" button.
     * Opens a popup overlay and fetches the list of available conversations.
     */
    $('#selectConversationBtn').on('click', function () {
        console.log("Select Conversation button clicked");
        $('#popupOverlay').fadeIn();
        fetchAvailableConversations();
    });

    /**
     * Fetches the list of available conversations from the server
     * and populates a dropdown menu with the results.
     */
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

    /**
     * Handles the submission of the selected conversation.
     * Loads and displays the conversation tree if a selection is made.
     */
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

    /**
     * Loads the conversation tree structure for the specified conversation ID.
     * Initializes jsTree to display nodes with custom icons and state handling.
     * @param {string} conversationId - The ID of the conversation to load.
     */
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
                            text: `<i class='fa fa-cog clickable-cog'></i> ${node.text}`, // Icons for parent nodes
                            icon: false,
                            state: node.state || {opened: false},
                            datums: node.datums,
                            children: node.children ? node.children.map(child => ({
                                id: child.id,
                                text: `<i class='fa fa-cog clickable-cog'></i> ${child.text}`, // Icons for child nodes
                                icon: false,
                                state: child.state || {opened: false},
                                datums: child.datums,
                                children: child.children || []
                            })) : []
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

    /**
     * Attaches click events to the cog icons within nodes to render their content.
     */
    function cogClicker() {
        $(document).on('click', '.clickable-cog', function (e) {
            e.stopPropagation();  // Prevent event from bubbling up to the node click event
            e.preventDefault();   // Prevent the default jsTree behavior

            // Find the closest `li` element (which represents the node in jsTree)
            let $nodeElement = $(this).closest('li');
            let nodeId = $nodeElement.attr('id');

            // Use jsTree's API to get the actual node object
            let tree = $('#conversationTree').jstree(true);  // Get the jsTree instance
            let node = tree.get_node(nodeId);  // Get the node object by its ID
            renderNodeContent(node);
        });
    }

    /**
     * Renders all nodes' content if needed, useful for preloading or displaying nodes.
     * This function is currently unused but can be enabled for pre-rendering content.
     */
    function renderAllNodes() {
        // Placeholder for rendering all nodes initially
    }

    /**
     * Renders the content for a specific jsTree node.
     * @param {Object} node - The jsTree node object to render.
     */
    function renderNodeContent(node) {
        console.log("Rendering content for node:", node.id);
        const nodeId = node.id;
        const nodeData = node.original.datums;

        const nodeContent = $('<div>').addClass('node-content');
        const nodeAttributes = $('<div>').addClass('node-attributes')
            .append($('<span>').addClass('node-date').text(' ' + nodeData.datetime));

        const nodeActions = $('<div>').addClass('node-actions')
            .append($('<button>').addClass('btn btn-primary btn-sm btn-save').text('Save'))
            .append($('<button>').addClass('btn btn-secondary btn-sm btn-copy').text('Copy'))
            .append($('<button>').addClass('btn btn-danger btn-sm btn-delete').text('Delete'))
            .append($('<button>').addClass('btn btn-secondary btn-sm btn-close').text('Close'));


        const nodeEditor = $('<div>').addClass('node-editor')
            .attr('contenteditable', 'true')
            .text(nodeData.content);

        nodeContent.append(nodeAttributes, nodeActions, nodeEditor);
        $("#elementDisplay").append(nodeContent);
        attachNodeEventHandlers(nodeId);
    }

    /**
     * Attaches event handlers to save, copy, delete, and close buttons within a node.
     * @param {string} nodeId - The ID of the node to attach event handlers to.
     */
    function attachNodeEventHandlers(nodeId) {
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
        //CHAT tried to delete this event - why???
        $(`#${nodeId} > .node-content`).on('click', function (e) {
            e.stopPropagation();
        });

    }

    function saveNodeContent(nodeId) {
        const content = $(`#${nodeId} .node-editor`).text();
        console.log("Saving content for node:", nodeId, "Content:", content);
        // Implement the save functionality as needed
    }

    /**
     * Copies specified text content to the clipboard and alerts the user.
     * @param {string} content - The content to copy to the clipboard.
     */
    function copyToClipboard(content) {
        navigator.clipboard.writeText(content).then(function () {
            console.log("Content copied to clipboard");
            alert('Content copied to clipboard!');
        }, function (err) {
            console.error('Could not copy text: ', err);
        });
    }

    /**
     * Deletes a specific node from the conversation tree.
     * @param {string} nodeId - The ID of the node to delete.
     */
    function deleteNode(nodeId) {
        if (confirm('Are you sure you want to delete this node?')) {
            $('#conversationTree').jstree(true).delete_node(nodeId);
            // Optionally make an AJAX call to delete the node on the server
            // Implement the actual delete functionality here
        }
    }

    /**
     * Closes the popup overlay without submitting data.
     */
    $('#closePopupBtn').on('click', function () {
        $('#popupOverlay').fadeOut();
    });

    /**
     * Example function to retrieve checked nodes from the jsTree.
     * Can be used to process selected nodes as needed.
     * @returns {Array} List of checked nodes.
     */
    function getCheckedNodes() {
        let checkedNodes = $('#conversationTree').jstree('get_checked', true);
        console.log("Checked Nodes:", checkedNodes);
        return checkedNodes;
    }

    $('#conversationTree').on('open_node.jstree close_node.jstree', function (e, data) {
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
