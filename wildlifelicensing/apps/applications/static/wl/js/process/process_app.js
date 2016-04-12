define(['jQuery', 'js/process/preview_versions', 'bootstrap', 'select2'], function ($, previewVersions) {
    var application, assessments, amendmentRequests, csrfToken;

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

        function initPreviousData(previousData) {
            $container = $('#lodgedVersionsBody');
            $.each(previousData, function(index, version) {
                var $versionContainer = $('<div></div>').addClass('lodged-version-row');
                $versionContainer.append($('<div></div>').addClass('lodged-version-col').text(version.lodgement_number));
                $versionContainer.append($('<div></div>').addClass('lodged-version-col').text(version.date));

                
                if(index === 0) {
                    var $compareLink = $('<a>Show</a>').addClass('hidden');
                    var $comparingSpan = $('<span>Showing</span>');
                } else {
                    var $compareLink = $('<a>Compare</a>');
                    var $comparingSpan = $('<span>Comparing</span>').addClass('hidden');
                }

                $compareLink.click(function(e) {
                    $container.find('a').removeClass('hidden');
                    $container.find('span').addClass('hidden');
                    $compareLink.addClass('hidden');
                    $comparingSpan.removeClass('hidden');
                    $previewContainer.empty();
                    previewVersions.layoutPreviewItems($previewContainer, data.form_structure, application.data, version.data);
                });

                $versionContainer.append($('<div></div>').addClass('lodged-version-col pull-right').append($compareLink).append($comparingSpan));

                $container.append($versionContainer);
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

                    application.id_check_status = data.id_check_status;
                    determineApplicationApprovable();
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

                    application.id_check_status = data.id_check_status;
                    determineApplicationApprovable();
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

                    application.character_check_status = data.character_check_status;
                    determineApplicationApprovable();
                });
            });
        }

        function prepareAmendmentRequestsPopover($showPopover) {
            var content = '';
            $.each(amendmentRequests, function(index, value) {
                content += '<p>' + value.text + '<p>';
            });

            // check if popover created yet
            var popover = $showPopover.data('bs.popover');
            if(popover === undefined) {
                $showPopover.popover({container: 'body', content: content, html: true});
                $showPopover.removeClass('hidden');
            } else {
                popover.options.content = content;
            }
        }

        function initReview() {
            var $container = $('#review');

            var $actionButtonsContainer = $container.find('.action-buttons-group'),
                $okTick = $container.find('.ok-tick'),
                $status = $container.find('.status'),
                $acceptButton = $actionButtonsContainer.find('.btn-success'),
                $requestAmendmentsButton = $actionButtonsContainer.find('.btn-warning'),
                $showAmendmentRequests = $container.find('a');

            if (application.review_status === 'Accepted') {
                $actionButtonsContainer.addClass('hidden');
                $status.addClass('hidden');
                $showAmendmentRequests.addClass('hidden');
                $okTick.removeClass('hidden');
                return;
            }

            $acceptButton.click(function(e) {
                $.post('/applications/set_review_status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'accepted'
                },
                function(data) {
                    $processingStatus.text(data.processing_status);
                    $status.addClass('hidden');
                    $actionButtonsContainer.addClass('hidden');
                    $showAmendmentRequests.addClass('hidden');
                    $okTick.removeClass('hidden');
                    application.review_status = data.review_status;
                    determineApplicationApprovable();
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

                    application.review_status = data.review_status;
                    determineApplicationApprovable();

                    if(data.review_status === 'Awaiting Amendments') {
                        amendmentRequests.push(data.amendment_request);
                        prepareAmendmentRequestsPopover($showAmendmentRequests);
                    }
                });
            });

            if(amendmentRequests.length > 0) {
                prepareAmendmentRequestsPopover($showAmendmentRequests);
            }
        }

        function createAssessmentRow(assessment) {
            var row = $('<tr></tr>');
            row.append('<td>' + assessment.assessor.first_name + ' ' + assessment.assessor.last_name + '</td>');
            var statusColumn = $('<td></td>').css('text-align', 'right');
            if(assessment.status === 'Awaiting Assessment') {
                statusColumn.append(assessment.status);
            } else {
                statusColumn.append('<a>View Comments</a>');
            }

            row.append(statusColumn);

            return row;
        }

        function initAssessment(assessorsList) {
            var $assessor = $('#assessor'),
                $sendForAssessment = $('#sendForAssessment'),
                $currentAssessments = $('#currentAssessments');

            $assessor.select2({
                data: assessorsList,
            });

            if(assessments.length > 0) {
                $.each(assessments, function(index, assessment) {
                    $currentAssessments.append(createAssessmentRow(assessment));
                });
                $currentAssessments.parent().removeClass('hidden');
            }

            $assessor.on('change', function(e) {
                $sendForAssessment.prop('disabled', false);
            });

            $sendForAssessment.click(function(e) {
                $.post('/applications/send_for_assessment/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'awaiting_assessment',
                    userID: $assessor.val()
                },
                function(data) {
                    $processingStatus.text(data.processing_status);
                    $currentAssessments.append(createAssessmentRow(data.assessment));
                    $assessor.select2('val', '');

                    // remove assessor from assessors list
                    for(var i = 0; i < assessorsList.length; i++) {
                        if(assessorsList[i].id === data.assessment.assessor.id) {
                            assessorsList.splice(i, 1);
                            break;
                        }
                    }

                    $currentAssessments.parent().removeClass('hidden');

                    assessments.push(data.assessment);
                    determineApplicationApprovable();
                });

                $sendForAssessment.prop('disabled', true);
            });
        }

        function determineApplicationApprovable() {
            var approvable = false;

            if((application.licence_type.identification_required && application.id_check_status === 'Accepted') || 
                    !application.licence_type.identification_required) {
                if(application.character_check_status === 'Accepted') {
                    if(application.review_status === 'Accepted') {
                        if(assessments.length === 0) {
                            approvable = true;
                        } else {
                            var allAssessed = true;
                            for(var i = 0; i < assessments.length; i++) {
                                if(assessments[i].status !== 'Assessed') {
                                    allAssessed = false;
                                    break;
                                }
                            }
                            approvable = allAssessed;
                        }
                    }
                }
            }

            $('#approve').prop('disabled', !approvable);
        }

        return {
            initialiseApplicationProcesssing: function (data) {
                $processingStatus = $('#processingStatus');
                $previewContainer = $('#previewContainer')
                csrfToken = data.csrf_token;
                application = data.application;
                assessments = data.assessments;
                amendmentRequests = data.amendment_requests;

                initAssignee(data.officers, data.user);
                initPreviousData(data.previous_application_data);
                initIDCheck();
                initCharacterCheck();
                initReview();
                initAssessment(data.assessors);

                determineApplicationApprovable();

                previewVersions.layoutPreviewItems($previewContainer, data.form_structure, application.data, application.data);
            },
            initialiseSidePanelAffix: function () {
                var $sidebarPanels = $('#sidebarPanels');
                $sidebarPanels.affix({ offset: { top: $sidebarPanels.offset().top }});
            }
        }
    });
