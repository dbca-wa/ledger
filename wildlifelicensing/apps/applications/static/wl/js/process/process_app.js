define(['jQuery', 'lodash', 'bootstrap', 'select2'], function ($, _) {
    var application;
    var csrfToken;

    var $processingStatus;

    function initAssignee(officersList, user) {
            var $assignee = $('#assignee');

            $assignee.select2({
                data: officersList,
                initSelection: function(element, callback) {
                    if(application.assigned_officer) {
                        callback({id:application.assigned_officer.id, text: application.assigned_officer.first_name + ' ' +
                                 application.assigned_officer.last_name});
                    } else {
                        callback({id: 0, text: 'Unassigned'});
                    }
                }
            });

            $assignee.on('change', function(e) {
                $.post('/applications/assign_officer/', {
                        applicationID: application.id,
                        csrfmiddlewaretoken: csrfToken,
                        userID: e.val
                    },
                    function(data) {
                        $processingStatus.text(data.processing_status);
                    }
                );
            });

            $('#assignToMe').click(function() {
                $.post('/applications/assign_officer/', {
                        applicationID: application.id,
                        csrfmiddlewaretoken: csrfToken,
                        userID: user.id
                    }, 
                    function(data) {
                        $assignee.select2('data', data.assigned_officer);
                        $processingStatus.text(data.processing_status);
                    }
                );
            });
        }

        function initIDCheck() {
            var $container = $('#idCheck');

            if(!application.licence_type.identification_required) {
                $container.addClass('hidden');
                return;
            }

            var $actionButtonsContainer = $container.find('.action-buttons-group'),
                $okTick = $container.find('.ok-tick'),
                $status = $container.find('.status');

            if (application.id_check_status === 'Accepted') {
                $actionButtonsContainer.addClass('hidden');
                $status.addClass('hidden');
                $okTick.removeClass('hidden');
                return;
            }

            var $acceptButton = $actionButtonsContainer.find('.btn-success'),
                $requestUpdateButton = $actionButtonsContainer.find('.btn-warning');

            $acceptButton.click(function(e) {
                $.post('/applications/set_id_check_status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'accepted'
                },
                function(data) {
                    $processingStatus.text(data.processing_status);
                    $status.addClass('hidden');
                    $okTick.removeClass('hidden');
                    $actionButtonsContainer.addClass('hidden');
                });
            });

            var $requestIDUpdateModal = $('#requestIDUpdateModal'),
                $requestIDUpdateSendButton = $requestIDUpdateModal.find('#sendIDUpdateRequest'),
                $requestIDUpdateMessage = $requestIDUpdateModal.find('textarea');

            $requestUpdateButton.click(function(e) {
                $requestIDUpdateModal.modal('show');
            });

            $requestIDUpdateSendButton.click(function(e) {
                $.post('/applications/set_id_check_status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'awaiting_update',
                    message: $requestIDUpdateMessage.val()
                },
                function(data) {
                    $processingStatus.text(data.processing_status);
                    $container.find('.status').text(data.id_check_status);
                    $requestIDUpdateMessage.val('');
                });
            });
        }

        function initCharacterCheck() {
            var $container = $('#characterCheck'),
                $actionButtonsContainer = $container.find('.action-buttons-group'),
                $okTick = $container.find('.ok-tick'),
                $status = $container.find('.status');

            if (application.character_check_status === 'Accepted') {
                $actionButtonsContainer.addClass('hidden');
                $status.addClass('hidden');
                $okTick.removeClass('hidden');
                return;
            }

            var $acceptButton = $actionButtonsContainer.find('.btn-success');

            $acceptButton.click(function(e) {
                $.post('/applications/set_character_check_status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'accepted'
                },
                function(data) {
                    $processingStatus.text(data.processing_status);
                    $status.addClass('hidden');
                    $okTick.removeClass('hidden');
                    $actionButtonsContainer.addClass('hidden');
                });
            });
        }

        function initReview() {
            var $container = $('#review');

            var $actionButtonsContainer = $container.find('.action-buttons-group'),
                $okTick = $container.find('.ok-tick'),
                $status = $container.find('.status');

            if (application.review_status === 'Accepted') {
                $actionButtonsContainer.addClass('hidden');
                $status.addClass('hidden');
                $okTick.removeClass('hidden');
                return;
            }

            var $acceptButton = $actionButtonsContainer.find('.btn-success'),
                $requestAmendmentsButton = $actionButtonsContainer.find('.btn-warning');

            $acceptButton.click(function(e) {
                $.post('/applications/set_review_status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'accepted'
                },
                function(data) {
                    $processingStatus.text(data.processing_status);
                    $status.addClass('hidden');
                    $okTick.removeClass('hidden');
                    $actionButtonsContainer.addClass('hidden');
                });
            });

            var $requestAmendmentsModal = $('#requestAmendmentsModal'),
                $requestAmendmentsSendButton = $requestAmendmentsModal.find('#sendAmendmentsRequest'),
                $requestAmendmentsMessage = $requestAmendmentsModal.find('textarea');

            $requestAmendmentsButton.click(function(e) {
                $requestAmendmentsModal.modal('show');
            });

            $requestAmendmentsSendButton.click(function(e) {
                $.post('/applications/set_review_status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'awaiting_amendments',
                    message: $requestAmendmentsMessage.val()
                },
                function(data) {
                    $processingStatus.text(data.processing_status);
                    $container.find('.status').text(data.review_status);
                    $requestAmendmentsMessage.val('');
                });
            });
        }

        return {
            initialiseApplicationProcesssing: function (data) {
                $processingStatus = $('#processingStatus');
                csrfToken = data.csrf_token;
                application = data.application;

                initAssignee(data.officers, data.user);
                initIDCheck();
                initCharacterCheck();
                initReview();
            },
            initialiseSidePanelAffix: function () {
                var $sidebarPanels = $('#sidebarPanels');
                $sidebarPanels.affix({ offset: { top: $sidebarPanels.offset().top }});
            }
        }
    });
