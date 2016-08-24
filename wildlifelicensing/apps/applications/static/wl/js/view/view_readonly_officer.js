define(['jQuery', 'lodash', 'js/entry/application_preview', 'select2'], function($, _, applicationPreview) {
    function initAssessorsCommentsPopover(assessments) {
        var $contentContainer = $('<div>'),
            $viewAssessorsComments = $('#viewAssessorsComments');

        if(assessments.length) {
            $.each(assessments, function(index, assessment) {
                if(assessment.status === 'Assessed') {
                    var assessorGroupName = '<strong>' + assessment.assessor_group.name + ': </strong>';
                    $contentContainer.append($('<p>').html(assessorGroupName + assessment.comment));
                }
            })
        }

        if ($contentContainer.children().length) {
            $contentContainer.find(':last-child').addClass('no-margin');
        } else {
            $contentContainer.append($('<p>').addClass('no-margin').text("No other assessors' comments available"));
        }

        $viewAssessorsComments.popover({container: 'body', content: $contentContainer, html: true});
    }

    return {
        init: function(application, assessments) {
            applicationPreview.layoutPreviewItems('#applicationContainer', application.licence_type.application_schema,
                    application.data);
            initAssessorsCommentsPopover(assessments);
        }
    }
});