define([
    'jQuery',
    'js/process/preview_versions',
    'js/wl.dataTable',
    'moment',
    'lodash',
    'bootstrap',
    'select2'
], function ($, previewVersions, dataTable, moment, _) {

    "use strict";

    var application, assessments, amendmentRequests, csrfToken, $processingStatus, $previewContainer, moduleData;

    function initAssignee(officersList, user) {
        var $assignee = $('#assignee');

        $assignee.select2({
            data: officersList,
            initSelection: function (element, callback) {
                if (application.assigned_officer) {
                    callback({
                        id: application.assigned_officer.id, text: application.assigned_officer.first_name + ' ' +
                        application.assigned_officer.last_name
                    });
                } else {
                    callback({id: 0, text: 'Unassigned'});
                }
            }
        });

        $assignee.on('change', function (e) {
            $.post('/applications/assign-officer/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    userID: e.val
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                }
            );
        });

        $('#assignToMe').click(function () {
            $.post('/applications/assign-officer/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    userID: user.id
                },
                function (data) {
                    $assignee.select2('data', data.assigned_officer);
                    $processingStatus.text(data.processing_status);
                }
            );
        });
    }

    function initLodgedVersions(previousData) {
        var $table = $('#lodgedVersions');
        $.each(previousData, function (index, version) {
            var $row = $('<tr>'), $compareLink, $comparingText, $actionSpan;

            $row.append($('<td>').text(version.lodgement_number));
            $row.append($('<td>').text(version.date));

            if (index === 0) {
                $compareLink = $('<a>').text('Show').addClass('hidden');
                $comparingText = $('<p>').css('font-style', 'italic').text('Showing').addClass('no-margin');

                $row.addClass('small-table-selected-row');
            } else {
                $compareLink = $('<a>').text('Compare');
                $comparingText = $('<p>').css('font-style', 'italic').text('Comparing').addClass('no-margin').addClass('hidden');
            }

            $actionSpan = $('<span>').append($compareLink).append($comparingText);

            $compareLink.click(function (e) {
                $(document).trigger('application-version-selected');
                $row.addClass('small-table-selected-row');
                $compareLink.addClass('hidden');
                $comparingText.removeClass('hidden');
                $previewContainer.empty();
                previewVersions.layoutPreviewItems($previewContainer, moduleData.form_structure, application.data, version.data);
            });

            $row.append($('<td>').html($actionSpan));

            $table.append($row);
        });

        $(document).on('application-version-selected', function() {
            $table.find('tr').removeClass('small-table-selected-row');
            $table.find('a').removeClass('hidden');
            $table.find('p').addClass('hidden');
        });
    }

    function initPreviousApplication() {
        if(!application.previous_application) {
            return;
        }

        var $table = $('#previousApplication');

        var $row = $('<tr>'), $compareLink;
        $row.append($('<td>').text(application.previous_application.lodgement_number));
        $row.append($('<td>').text(application.previous_application.lodgement_date));

        var $compareLink = $('<a>Compare</a>');

        var $comparingText = $('<p>').css('font-style', 'italic').text('Comparing').addClass('no-margin').addClass('hidden');

        var $actionSpan = $('<span>').append($compareLink).append($comparingText);

        $compareLink.click(function (e) {
            $(document).trigger('application-version-selected');
            $row.addClass('small-table-selected-row');
            $compareLink.addClass('hidden');
            $comparingText.removeClass('hidden');
            $previewContainer.empty();
            previewVersions.layoutPreviewItems($previewContainer, moduleData.form_structure, application.data, application.previous_application.data);
        });

        $row.append($('<td>').html($actionSpan));

        $table.append($row);

        $(document).on('application-version-selected', function() {
            $table.find('tr').removeClass('small-table-selected-row');
            $compareLink.removeClass('hidden');
            $comparingText.addClass('hidden');
        });
    }

    function initIDCheck() {
        var $container = $('#idCheck');

        if (!application.licence_type.identification_required) {
            $container.addClass('hidden');
            return;
        }

        var $actionButtonsContainer = $container.find('.action-buttons-group'),
            $done = $container.find('.done'),
            $resetLink = $done.find('a'),
            $status = $container.find('.status');

        if (application.id_check_status === 'Accepted') {
            $actionButtonsContainer.addClass('hidden');
            $status.addClass('hidden');
            $done.removeClass('hidden');
        }

        $resetLink.click(function () {
            $.post('/applications/set-id-check-status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'not_checked'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $actionButtonsContainer.removeClass('hidden');
                    $status.text(data.id_check_status);
                    $status.removeClass('hidden');
                    $done.addClass('hidden');

                    application.id_check_status = data.id_check_status;
                    determineApplicationApprovable();
                });
        });

        var $acceptButton = $actionButtonsContainer.find('.btn-success'),
            $requestUpdateButton = $actionButtonsContainer.find('.btn-warning');

        $acceptButton.click(function () {
            $.post('/applications/set-id-check-status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'accepted'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $status.addClass('hidden');
                    $done.removeClass('hidden');
                    $actionButtonsContainer.addClass('hidden');

                    application.id_check_status = data.id_check_status;
                    determineApplicationApprovable();
                });
        });

        var $requestIDUpdateModal = $('#requestIDUpdateModal'),
            $idRequestForm = $requestIDUpdateModal.find('#idRequestForm'),
            $idReason = $idRequestForm.find('#id_reason'),
            $idText = $idRequestForm.find('#id_text');

        $requestUpdateButton.click(function () {
            $requestIDUpdateModal.modal('show');
        });

        $idRequestForm.submit(function (e) {
            $.ajax({
                type: $(this).attr('method'),
                url: $(this).attr('action'),
                data: $(this).serialize(),
                success: function (data) {
                    $processingStatus.text(data.processing_status);
                    $container.find('.status').text(data.id_check_status);
                    $idReason.find('option:eq(0)').prop('selected', true);
                    $idText.val('');

                    application.id_check_status = data.id_check_status;
                    determineApplicationApprovable();

                    $requestIDUpdateModal.modal('hide');
                }
            });

            e.preventDefault();
        });
    }

    function initReturnsCheck() {
        var $container = $('#returnsCheck');

        // for new applications or applications that are licence amendments, no need to check returns
        if (application.application_type !== 'renewal') {
            $container.addClass('hidden');
            return;
        }

        var $actionButtonsContainer = $container.find('.action-buttons-group'),
            $done = $container.find('.done'),
            $resetLink = $done.find('a'),
            $status = $container.find('.status');

        if (application.returns_check_status === 'Accepted') {
            $actionButtonsContainer.addClass('hidden');
            $status.addClass('hidden');
            $done.removeClass('hidden');
        }

        $resetLink.click(function () {
            $.post('/applications/set-returns-check-status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'not_checked'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $actionButtonsContainer.removeClass('hidden');
                    $status.text(data.returns_check_status);
                    $status.removeClass('hidden');
                    $done.addClass('hidden');

                    application.returns_check_status = data.returns_check_status;
                    determineApplicationApprovable();
                });
        });

        var $acceptButton = $actionButtonsContainer.find('.btn-success'),
            $requestReturnsButton = $actionButtonsContainer.find('.btn-warning');

        $acceptButton.click(function () {
            $.post('/applications/set-returns-check-status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'accepted'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $status.addClass('hidden');
                    $done.removeClass('hidden');
                    $actionButtonsContainer.addClass('hidden');

                    application.returns_check_status = data.returns_check_status;
                    determineApplicationApprovable();
                });
        });

        var $requestReturnsModal = $('#requestReturnsModal'),
            $returnsRequestForm = $requestReturnsModal.find('#returnsRequestForm'),
            $returnsReason = $returnsRequestForm.find('#id_reason'),
            $returnsText = $returnsRequestForm.find('#id_text');

        $requestReturnsButton.click(function () {
            $requestReturnsModal.modal('show');
        });

        $returnsRequestForm.submit(function (e) {
            $.ajax({
                type: $(this).attr('method'),
                url: $(this).attr('action'),
                data: $(this).serialize(),
                success: function (data) {
                    $processingStatus.text(data.processing_status);
                    $container.find('.status').text(data.returns_check_status);
                    $returnsReason.find('option:eq(0)').prop('selected', true);
                    $returnsText.val('');

                    application.returns_check_status = data.returns_check_status;
                    determineApplicationApprovable();

                    $requestReturnsModal.modal('hide');
                }
            });

            e.preventDefault();
        });
    }

    function initCharacterCheck() {
        var $container = $('#characterCheck'),
            $actionButtonsContainer = $container.find('.action-buttons-group'),
            $done = $container.find('.done'),
            $resetLink = $done.find('a'),
            $status = $container.find('.status'),
            $showCharacterChecklist = $container.find('#showCharacterChecklist'),
            $dodgyUser = $container.find('#dodgyUser');

        if (application.character_check_status === 'Accepted') {
            $actionButtonsContainer.addClass('hidden');
            $status.addClass('hidden');
            $showCharacterChecklist.addClass('hidden');
            $dodgyUser.addClass('hidden');
            $done.removeClass('hidden');
        }

        $resetLink.click(function () {
            $.post('/applications/set-character-check-status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'not_checked'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $actionButtonsContainer.removeClass('hidden');
                    $status.text(data.character_check_status);
                    $status.removeClass('hidden');
                    $showCharacterChecklist.removeClass('hidden');
                    if (application.applicant_profile.user.character_flagged) {
                        $dodgyUser.removeClass('hidden');
                    }

                    $done.addClass('hidden');

                    application.character_check_status = data.character_check_status;
                    determineApplicationApprovable();
                });
        });

        var $acceptButton = $actionButtonsContainer.find('.btn-success');

        $acceptButton.click(function () {
            $.post('/applications/set-character-check-status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'accepted'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $status.addClass('hidden');
                    $done.removeClass('hidden');
                    $actionButtonsContainer.addClass('hidden');
                    $showCharacterChecklist.addClass('hidden');
                    $dodgyUser.addClass('hidden');

                    application.character_check_status = data.character_check_status;
                    determineApplicationApprovable();
                });
        });

        var $characterChecklist = $('<ul>').addClass('popover-checklist');

        $characterChecklist.append($('<li>').text('Character flag in database'));
        $characterChecklist.append($('<li>').text('Police record check'));

        $showCharacterChecklist.popover({
            container: 'body',
            content: $characterChecklist.prop('outerHTML'),
            html: true
        });

        if (application.applicant_profile.user.character_flagged) {
            $dodgyUser.tooltip({container: 'body'});
        }
    }

    function prepareAmendmentRequestsPopover($showPopover) {
        var $content = $('<ul>').addClass('popover-checklist');
        $.each(amendmentRequests, function (index, value) {
            $content.append($('<li>').text(value.reason + ': ' + value.text));
        });

        // check if popover created yet
        var popover = $showPopover.data('bs.popover');
        if (popover === undefined) {
            $showPopover.popover({container: 'body', content: $content.prop('outerHTML'), html: true});
            $showPopover.removeClass('hidden');
        } else {
            popover.options.content = $content;
        }
    }

    function initReview() {
        var $container = $('#review');

        var $actionButtonsContainer = $container.find('.action-buttons-group'),
            $done = $container.find('.done'),
            $status = $container.find('.status'),
            $acceptButton = $actionButtonsContainer.find('.btn-success'),
            $resetLink = $done.find('a'),
            $requestAmendmentButton = $actionButtonsContainer.find('.btn-warning'),
            $showAmendmentRequests = $container.find('#showAmendmentRequests');

        if (amendmentRequests.length > 0) {
            prepareAmendmentRequestsPopover($showAmendmentRequests);
        }

        if (application.review_status === 'Accepted') {
            $actionButtonsContainer.addClass('hidden');
            $status.addClass('hidden');
            $showAmendmentRequests.addClass('hidden');
            $done.removeClass('hidden');
        }

        $resetLink.click(function () {
            $.post('/applications/set-review-status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'not_reviewed'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $actionButtonsContainer.removeClass('hidden');
                    $status.text(data.review_status);
                    $status.removeClass('hidden');
                    if (amendmentRequests.length > 0) {
                        $showAmendmentRequests.removeClass('hidden');
                    }
                    $done.addClass('hidden');

                    application.review_status = data.review_status;
                    determineApplicationApprovable();
                });
        });

        $acceptButton.click(function () {
            $.post('/applications/set-review-status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'accepted'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $status.addClass('hidden');
                    $actionButtonsContainer.addClass('hidden');
                    $showAmendmentRequests.addClass('hidden');
                    $done.removeClass('hidden');
                    application.review_status = data.review_status;
                    determineApplicationApprovable();
                });
        });

        var $requestAmendmentModal = $('#requestAmendmentModal'),
            $amendmentRequestForm = $requestAmendmentModal.find('#amendmentRequestForm'),
            $idReason = $amendmentRequestForm.find('#id_reason'),
            $idText = $amendmentRequestForm.find('#id_text');

        $requestAmendmentButton.click(function () {
            $requestAmendmentModal.modal('show');
        });

        $amendmentRequestForm.submit(function (e) {
            $.ajax({
                type: $(this).attr('method'),
                url: $(this).attr('action'),
                data: $(this).serialize(),
                success: function (data) {
                    $processingStatus.text(data.processing_status);
                    $status.text(data.review_status);
                    $idReason.find('option:eq(0)').prop('selected', true);
                    $idText.val('');

                    application.review_status = data.review_status;
                    determineApplicationApprovable();

                    if (data.review_status === 'Awaiting Amendments') {
                        amendmentRequests.push(data.amendment_request);
                        prepareAmendmentRequestsPopover($showAmendmentRequests);
                    }

                    $requestAmendmentModal.modal('hide');
                }
            });

            e.preventDefault();
        });
    }

    function createAssessmentRow(assessment) {
        var $row = $('<tr>'),
            $statusColumn = $('<td>').addClass('center'),
            $remind = $('<p>').addClass('center').addClass('no-margin').append($('<a>').text('Remind')),
            $reassess = $('<p>').addClass('center').addClass('no-margin').append($('<a>').text('Reassess'));

        $row.append('<td>' + assessment.assessor_group.name + '</td>');

        $remind.click(function () {
            $.post('/applications/remind-assessment/', {
                assessmentID: assessment.id,
                csrfmiddlewaretoken: csrfToken
            }, function (data) {
                if (data === 'ok') {
                    window.alert('Reminder sent');
                }
            });
        });

        $reassess.click(function () {
            $.post('/applications/send-for-assessment/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    assGroupID: assessment.assessor_group.id
                },
                function (data) {
                    $processingStatus.text(data.processing_status);

                    $statusColumn.empty();
                    $statusColumn.append(data.assessment.status);
                    $statusColumn.append($remind);

                    determineApplicationApprovable();
                }
            );
        });

        $statusColumn.append(assessment.status);

        if (assessment.status === 'Awaiting Assessment') {
            $statusColumn.append($remind);
        } else {
            if (assessment.comment) {
                var $viewComment = $('<p>').addClass('center').addClass('no-margin').append(
                        $('<a>').text('View Comment').attr('data-toggle', 'popover'));
                $viewComment.popover({container: 'body', content: assessment.comment, html: true});
                $statusColumn.append($viewComment);
            }
            $statusColumn.append($reassess);
        }

        $row.append($statusColumn);
        return $row;
    }

    function initAssessment(assessorsList) {
        var $assessor = $('#assessor'),
            $sendForAssessment = $('#sendForAssessment'),
            $currentAssessments = $('#currentAssessments');

        $assessor.select2({
            data: assessorsList
        });

        if (assessments.length > 0) {
            $.each(assessments, function (index, assessment) {
                $currentAssessments.append(createAssessmentRow(assessment));
            });
            $currentAssessments.parent().removeClass('hidden');
        }

        $assessor.on('change', function () {
            $sendForAssessment.prop('disabled', false);
        });

        $sendForAssessment.click(function () {
            $.post('/applications/send-for-assessment/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    assGroupID: $assessor.val()
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $currentAssessments.append(createAssessmentRow(data.assessment));
                    $assessor.select2('val', '');

                    // remove assessor from assessors list
                    for (var i = 0; i < assessorsList.length; i++) {
                        if (assessorsList[i].id === data.assessment.assessor_group.id) {
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
        var $submissionForm = $('#submissionForm'),
            $approve = $submissionForm.find('#approve'),
            $decline = $submissionForm.find('#decline'),
            $buttonClicked,
            approvableConditions = [
                (application.licence_type.identification_required && application.id_check_status === 'Accepted') || !application.licence_type.identification_required,
                (application.application_type === 'renewal' && application.returns_check_status === 'Accepted') || application.application_type != 'renewal',
                application.character_check_status === 'Accepted',
                application.review_status === 'Accepted'
            ];

        // ensure form only submits when either approve (enterConditions) is enabled or decline is clicked
        $($approve).click(function() {
            $buttonClicked = $(this);
        });

        $($decline).click(function() {
            $buttonClicked = $(this);
            declineApplication();
        });

        $submissionForm.submit(function(e) {
            if($buttonClicked.is($approve) && $approve.hasClass('disabled')) {
                e.preventDefault();
            }
        });

        if(_.every(approvableConditions)) {
            $approve.removeClass('disabled');
            $approve.tooltip('destroy');
        } else {
            $approve.addClass('disabled');
            $approve.tooltip({});
        }
    }

    function declineApplication() {
        var $modal =  $('#declinedDetailsModal');
        $modal.modal('show');
    }

    return {
        initialiseApplicationProcesssing: function (data) {
            $processingStatus = $('#processingStatus');
            $previewContainer = $('#previewContainer');
            csrfToken = data.csrf_token;
            application = data.application;
            assessments = data.assessments;
            amendmentRequests = data.amendment_requests;
            moduleData = data;

            initAssignee(data.officers, data.user);
            initLodgedVersions(data.previous_versions);
            initPreviousApplication();
            initIDCheck();
            initReturnsCheck();
            initCharacterCheck();
            initReview();
            initAssessment(data.assessor_groups);
            determineApplicationApprovable();

            previewVersions.layoutPreviewItems($previewContainer, data.form_structure, application.data, application.data);
        },
        initialiseSidePanelAffix: function () {
            var $sidebarPanels = $('#sidebarPanels');
            $sidebarPanels.affix({offset: {top: $sidebarPanels.offset().top}});
        }
    };
});
