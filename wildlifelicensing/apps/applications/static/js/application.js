define(['jQuery', 'handlebars', 'parsley', 'bootstrap', 'bootstrap-datetimepicker', 'select2', 'js/handlebars_helpers'], function($, Handlebars) {
    var templates = {};
    var applicationData = {}

    function _getTemplate(templateName) {
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

    function _layoutItem(item, parentAnchorPointSelector, parentItemID, index, repetitionIndex) {
        var itemContainer = $('<div>');

        item.id = parentItemID + '-' + index;

        $(parentAnchorPointSelector).append(itemContainer);

        // if this is a repeatable item (such as a group), add repetitionIndex to item ID
        if(item.isRepeatable) {
            repetitionIndex = repetitionIndex !== undefined ? repetitionIndex: 0;
            item.id += '-repeat-' + repetitionIndex;
            if(repetitionIndex > 0) {
                item.isRemovable = true;
            }
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

        itemContainer.append(_getTemplate(item.type)(item));

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
                itemContainer.append(childrenAnchorPoint);
            }

            if(item.condition !== undefined) {
                var inputSelector = itemContainer.find('input, select');

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
            _layoutChildren(item.children, childrenAnchorPoint, item.id);
        }

        // if item is a section, need to add to side menu list
        if(item.type === 'section') {
            var link = $('<a>');
            link.attr('href', '#' + item.id);
            link.text(item.label);
            $('#sectionList ul').append($('<li>').append(link));
        } else if(item.type === 'group' && item.isRepeatable) { 
            if(repetitionIndex === 0) {
                var addGroupDiv = $('<div>').addClass('add-group');
                var addGroupLink = $('<a>').text('Add ' + item.label);
                itemContainer.after(addGroupDiv.append(addGroupLink));

                var repeatItemsAnchorPoint = $('<div>').attr('id', item.name + '-repeated-items');
                itemContainer.after(repeatItemsAnchorPoint);

                addGroupLink.click(function(e) {
                    _layoutItem(item, repeatItemsAnchorPoint, parentItemID, index, ++repetitionIndex);
                });
            }

            if(repeatItemsAnchorPoint === undefined) {
                repeatItemsAnchorPoint = $('#'+ item.name + "-repeated-items")
            }

            if(applicationData != undefined && item.name in applicationData && repetitionIndex < applicationData[item.name].length - 1) {
                _layoutItem(item, repeatItemsAnchorPoint, parentItemID, index, ++repetitionIndex);
            }

            _setupCloneRemoveEvents(itemContainer);
        }
    }

    function _setupCloneRemoveEvents(itemSelector) {
    	itemSelector.find("[id$='copy']").click(function(e) {
            var itemClone = itemSelector.clone();
            itemSelector.find('select').each(function() {
            	selectSelectorClone = itemClone.find("[name='" + $(this).attr('name') + "']");
            	selectSelectorClone.val($(this).val());
            });
            itemClone.find('.hidden').removeClass('hidden');
            itemSelector.after(itemClone);
            _setupCloneRemoveEvents(itemClone);
        });

    	itemSelector.find("[id$='remove']").click(function(e) {
    		itemSelector.remove();
        });

        // initialise all datapickers
    	itemSelector.find('.date').datetimepicker({
            format: 'DD/MM/YYYY'
        });
    }

    function _layoutChildren(children, childrenAnchorPointID, itemID) {
        $.each(children, function(index, child) {
            _layoutItem(child, childrenAnchorPointID, itemID, index);
        });
    }

    return function(mainContainerSelector, formStructure, csrfToken, userSelectionRequired, data) {
        formStructure.csrfToken = csrfToken;
        $(mainContainerSelector).append(_getTemplate('application')(formStructure));

        applicationData = data;

        if(userSelectionRequired) {
            var itemContainer = $('<div>');
            $('#' + formStructure.childrenAnchorPointID).append(itemContainer);
            itemContainer.append(_getTemplate('applicant_section')({}));

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

        _layoutChildren(formStructure.children, '#' + formStructure.childrenAnchorPointID, 'item', 0);

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