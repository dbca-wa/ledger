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
            $.post('/applications/assign_officer/', {
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
            $.post('/applications/assign_officer/', {
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

    function createVersionRow(assessment) {
        var row = $('<tr></tr>');
        row.append('<td>' + assessment.assessor.first_name + ' ' + assessment.assessor.last_name + '</td>');
        var statusColumn = $('<td></td>').css('text-align', 'right');
        if (assessment.status === 'Awaiting Assessment') {
            statusColumn.append(assessment.status);
        } else {
            statusColumn.append('<a href="' + assessment.url + '">View Assessment</a>');
        }

        row.append(statusColumn);

        return row;
    }

    function initLodgedVersions(previousData) {
        var $table = $('#lodgedVersions');
        $.each(previousData, function (index, version) {
            var $row = $('<tr>'), $compareLink;
            $row.append($('<td>').text(version.lodgement_number));
            $row.append($('<td>').text(version.date));

            if (index === 0) {
                $compareLink = $('<a>Show</a>').addClass('hidden');
                $row.addClass('small-table-selected-row');
            } else {
                $compareLink = $('<a>Compare</a>');
            }

            $compareLink.click(function (e) {
                $table.find('tr').removeClass('small-table-selected-row');
                $table.find('a').removeClass('hidden');
                $row.addClass('small-table-selected-row');
                $row.find('a').addClass('hidden');
                $previewContainer.empty();
                previewVersions.layoutPreviewItems($previewContainer, moduleData.form_structure, application.data, version.data);
            });

            $row.append($('<td>').html($compareLink));

            $table.append($row);
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
            $.post('/applications/set_id_check_status/', {
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
            $.post('/applications/set_id_check_status/', {
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
            $.post('/applications/set_character_check_status/', {
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
            $.post('/applications/set_character_check_status/', {
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
            $.post('/applications/set_review_status/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'not_reviewed'
                },
                function (data) {
                    $processingStatus.text(data.processing_status);
                    $actionButtonsContainer.removeClass('hidden');
                    $status.text(data.review_status);
                    $status.removeClass('hidden');
                    $showAmendmentRequests.removeClass('hidden');
                    $done.addClass('hidden');

                    application.review_status = data.review_status;
                    determineApplicationApprovable();
                });
        });

        $acceptButton.click(function () {
            $.post('/applications/set_review_status/', {
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
            $actions = $('<p>').addClass('center').addClass('no-margin');
        $row.append('<td>' + assessment.assessor_group.name + '</td>');
        var statusColumn = $('<td>').addClass('center');
        if (assessment.status === 'Awaiting Assessment') {
            var $remind = $('<a>').text('Remind');

            $remind.click(function () {
                $.post('/applications/remind_assessment/', {
                    assessmentID: assessment.id,
                    csrfmiddlewaretoken: csrfToken
                }, function (data) {
                    if (data === 'ok') {
                        window.alert('Reminder sent');
                    }
                });
            });

            $actions.append($remind);
        } else {
            var $viewComment = $('<a>').text('View Comment');
            $viewComment.popover({container: 'body', content: assessment.comment, html: true});
            $actions.append($viewComment);
        }

        statusColumn.append(assessment.status);
        statusColumn.append($actions);

        $row.append(statusColumn);
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
            $.post('/applications/send_for_assessment/', {
                    applicationID: application.id,
                    csrfmiddlewaretoken: csrfToken,
                    status: 'awaiting_assessment',
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

    function initCommunicationLog() {

        var $showLogButton = $('#showLog'),
            $logEntryModal = $('#logEntryModal'),
            $logEntryForm = $logEntryModal.find('form'),
            $addLogEntryButton = $('#addLogEntry'),
            $logListContent = $('<div>'),
            $logTable = $('<table class="table table-bordered">');

        $logListContent.append($logTable);
        dataTable = initLogTable($logTable);
        $addLogEntryButton.click(function () {
            $logEntryModal.modal('show');
        });

        $showLogButton.popover({
            container: 'body',
            title: 'Communication log',
            content: $logListContent,
            placement: 'right',
            trigger: "manual",
            html: true
        }).click(function () {
            // Check popover visibility.
            var isVisible = $(this).data()['bs.popover'].tip().hasClass('in');
            if (!isVisible) {
                dataTable.ajax.reload();
                $showLogButton.popover('show');
                $('[data-toggle="tooltip"]').tooltip();
            } else {
                $showLogButton.popover('hide');
            }
        });

        $logEntryForm.submit(function (e) {
            var formData;
            e.preventDefault();
            formData = new FormData($(this).get(0));
            $.ajax({
                type: $(this).attr('method'),
                url: $(this).attr('action'),
                data: formData,
                processData: false,
                contentType: false,
                success: function () {
                    $logEntryModal.modal('hide');
                }
            });
        });
    }

    function initLogTable($table) {
        var dateFormat = 'DD/MM/YYYY',
            tableOptions = {
                paging: true,
                info: true,
                searching: true,
                processing: true,
                deferRender: true,
                serverSide: false,
                autowidth: true,
                order: [[0, 'desc']],
                ajax: {
                    url: '/applications/log_list/' + application.id
                }
            },
            colDefinitions = [
                {
                    title: 'Date',
                    data: 'date',
                    'render': function (date) {
                        return moment(date).format(dateFormat);
                    }
                },
                {
                    title: 'Type',
                    data: 'type'
                },
                {
                    title: 'Subject/Desc.',
                    data: 'subject'
                },
                {
                    title: 'Text',
                    data: 'text',
                    'render': function (value) {
                        var ellipsis = '...',
                            truncated = _.truncate(value, {
                            length: 100,
                            omission: ellipsis,
                            separator: ' '
                        }),
                            result = '<span>' + truncated +'</span>',
                            popTemplate = _.template('<a href="#" ' +
                                'role="button" ' +
                                'data-toggle="popover" ' +
                                'data-trigger="click" ' +
                                'data-placement="top auto"' +
                                'data-html="true" ' +
                                'data-content="<%= text %>" ' +
                                '>more</a>');
                        if (_.endsWith(truncated, ellipsis)) {
                            result += popTemplate({
                               text: value
                            });
                        }
                        return result;
                    },
                    'createdCell': function (cell) {
                        //TODO why this is not working?
                        // the call to popover is done in the 'draw' event
                        $(cell).popover();
                    }
                },
                {
                    title: 'Document',
                    data: 'document',
                    'render': function (value) {
                        if (value) {
                            return '<a href="' + value + '" target="_blank"><p>View</p></a>';
                        } else {
                            return '';
                        }
                    }
                }
            ];
        // set DT date format sorting
        dataTable.setDateTimeFormat(dateFormat);
        // activate popover when table is drawn.
        $table.on('draw.dt', function () {
            $table.find('[data-toggle="popover"]').popover();
        });
        return dataTable.initTable($table, tableOptions, colDefinitions);
    }


    function determineApplicationApprovable() {
        var approvable = false;

        if ((application.licence_type.identification_required && application.id_check_status === 'Accepted') || !application.licence_type.identification_required) {
            if (application.character_check_status === 'Accepted') {
                if (application.review_status === 'Accepted') {
                    approvable = true;
                }
            }
        }

        $('#approve').prop('disabled', !approvable);
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
            initLodgedVersions(data.previous_application_data);
            initIDCheck();
            initCharacterCheck();
            initReview();
            initAssessment(data.assessor_groups);
            initCommunicationLog();
            determineApplicationApprovable();

            previewVersions.layoutPreviewItems($previewContainer, data.form_structure, application.data, application.data);
        },
        initialiseSidePanelAffix: function () {
            var $sidebarPanels = $('#sidebarPanels');
            $sidebarPanels.affix({offset: {top: $sidebarPanels.offset().top}});
        }
    };
});
