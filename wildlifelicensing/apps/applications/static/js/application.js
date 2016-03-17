define(['jQuery', 'handlebars', 'parsley', 'bootstrap', 'bootstrap-datetimepicker', 'select2', 'js/handlebars_helpers'], function($, Handlebars) {
    var templates = {};
    var applicationData = {}

    function getTemplate(templateName) {
        if (templates[templateName] === undefined) {
            $.ajax({
                url: '/static/hdb_templates/' + templateName + '.handlebars',
                success: function(data) {
                    templates[templateName] = Handlebars.compile(data);
                },
                async: false
            });
        }

        return templates[templateName]
    }

    function layoutItem(item, parentAnchorPointSelector, parentItemID, index, repetitionIndex) {
        var itemDiv = $('<div>');

        item.id = parentItemID + '-' + index;

        // if this item is a repeat, insert after previous item, else append to parentAnchorPoint
        if(repetitionIndex !== undefined) {
            itemDiv.insertAfter($('#' + item.id + '-repeat-' + (repetitionIndex-1)));
        } else {
            $(parentAnchorPointSelector).append(itemDiv);
        }

        // if this is a repeatable item (such as a group), add repetitionIndex to item ID
        if(item.isRepeatable) {
            repetitionIndex = repetitionIndex !== undefined ? repetitionIndex: 0;
            item.id += '-repeat-' + repetitionIndex;
        }

        item.childrenAnchorPointID = item.id + '-children';

        // if there is application data available, add it to the item context so it can be reproduced in the template
        if((applicationData != undefined && item.name in applicationData) || item.data) {
            var data = item.name in applicationData ? applicationData[item.name] : item.data;

            // for groups, need to ascertain the relevant data and append to the group's children
            if (item.type === 'group') {
                repetitionIndex = repetitionIndex !== undefined ? repetitionIndex: 0;

                // if the repetitionIndex is less than the amount of data in the array of objects for this group, set the data value of each child element
                if(repetitionIndex < data.length) {
                    $.each(item.children, function(index, child) {
                        child.data = data[repetitionIndex][child.name];
                    });
                }
            } else {
                item.value = data;
            }
        }

        itemDiv.append(getTemplate(item.type)(item));

        // unset item value and data if they were set otherwise there may be unintended consequences if extra form fields are created dynamically
        item.value = undefined;
        item.data = undefined;

        if(item.children !== undefined) {
            var childrenAnchorPoint;

            // if no children anchor point was defined within the template, create one under current item
            if($('#' + item.childrenAnchorPointID).length) {
                childrenAnchorPoint = $('#' + item.childrenAnchorPointID);
            } else {
                childrenAnchorPoint = $('<div>');
                childrenAnchorPoint.addClass('children-anchor-point');
                childrenAnchorPoint.attr('id', item.id + '-children');
                itemDiv.append(childrenAnchorPoint);
            }

            if(item.condition !== undefined) {
                var inputSelector = itemDiv.find('input, select');

                // hide children initially if current item value does not equal condition
                if(inputSelector.val() !== item.condition) {
                    childrenAnchorPoint.hide();
                }

                inputSelector.change(function(e) {
                    if ($(this).val() === item.condition) {
                        childrenAnchorPoint.slideDown('medium');
                    } else {
                        childrenAnchorPoint.slideUp('medium');
                    }
                });
            }
            layoutChildren(item.children, childrenAnchorPoint, item.id);
        }

        // if item is a section, need to add to side menu list
        if(item.type === 'section') {
            var link = $('<a>');
            link.attr('href', '#' + item.id);
            link.text(item.label);
            $('#sectionList ul').append($('<li>').append(link));
        } else if(item.type === 'group' && item.isRepeatable && repetitionIndex === 0) {
            var addGroupDiv = $('<div>').addClass('add-group');
            var addGroupLink = $('<a>').text('Add ' + item.label);
            addGroupLink.click(function(e) {
                layoutItem(item, parentAnchorPointSelector, parentItemID, index, ++repetitionIndex);
            });
            itemDiv.append(addGroupDiv.append(addGroupLink));
        }
    }

    function layoutChildren(children, childrenAnchorPointID, itemID) {
        $.each(children, function(index, child) {
            layoutItem(child, childrenAnchorPointID, itemID, index);
        });
    }

    return function(mainContainerSelector, formStructure, csrfToken, userSelectionRequired, data) {
        formStructure.csrfToken = csrfToken;
        $(mainContainerSelector).append(getTemplate('application')(formStructure));

        applicationData = data;

        if(userSelectionRequired) {
            var itemDiv = $('<div>');
            $('#' + formStructure.childrenAnchorPointID).append(itemDiv);
            itemDiv.append(getTemplate('applicant_section')({}));

            $('#applicantInput').select2({
                ajax: {
                    url: "/applicants/",
                    dataType: 'json',
                    data: function (term) {
                        return {
                            term: term
                        };
                    },
                    results: function (data) {
                        return {
                            results: data
                        }
                    }
                },
                initSelection: function(element, callback) {
                    if(applicationData != undefined && 'applicant' in applicationData) {
                        $.ajax('/applicants/' + applicationData.applicant, {
                            dataType: 'json'
                        }).done(function(data) {
                            // set initial selection to first (and theoretically only) element
                            callback(data[0]);
                        });
                    }
                },
                minimumInputLength: 3
            });
        }

        layoutChildren(formStructure.children, '#' + formStructure.childrenAnchorPointID, 'item', 0);

        // initialise side-menu
        var sectionList = $('#sectionList');
        $('body').scrollspy({ target: '#sectionList' });
        sectionList.affix({ offset: { top: 200 }});

        // initialise all datapickers
        $('.date').datetimepicker({
            format: 'DD/MM/YYYY'
        });

        // initialise parsley form validation
        $('form').parsley({
            successClass: "has-success",
            errorClass: "has-error",
            classHandler: function(el) {
                return el.$element.closest(".form-group");
            },
            errorsContainer: function(el) {
                return el.$element.parents('.form-group');
            },
            errorsWrapper: '<span class="help-block">',
            errorTemplate: '<div></div>'
        }).on('field:validate', function(el) {
            // skip validation of invisible fields
            if (!el.$element.is(':visible')) {
                el.value = false;
                return true;
            }
        });
    };
});