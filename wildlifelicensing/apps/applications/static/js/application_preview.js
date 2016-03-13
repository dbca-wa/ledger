define(['jQuery', 'handlebars', 'bootstrap'], function($, Handlebars) {
    function layoutItem(item, data, parentAnchorPointSelector, parentItemID, index, repetitionIndex) {
        var itemDiv = $('<div>');

        item.id = parentItemID + '-' + index;

        // if this item is a repeat, insert after previous item, else append to parentAnchorPoint
//        if(repetitionIndex !== undefined) {
//            itemDiv.insertAfter($('#' + item.id + '-repeat-' + (repetitionIndex-1)));
//        } else {
            $(parentAnchorPointSelector).append(itemDiv);
//        }
//
//        // if this is a repeatable item (such as a group), add repetitionIndex to item ID
//        if(item.isRepeatable) {
//            if(repetitionIndex === undefined) {
//                repetitionIndex = 0;
//            }
//            item.id += '-repeat-' + repetitionIndex;
//        }

        item.childrenAnchorPointID = item.id + '-children';

        itemDiv.append($('<label>').text(item.label));//getTemplate(item.type)(item));
        itemDiv.append($('<p>').text(data[item.name]));

        if(item.children !== undefined) {
            var childrenAnchorPoint;

            // if no children anchor point was defined in the template, create one under current item
            if($('#' + item.childrenAnchorPointID).length) {
                childrenAnchorPoint = $('#' + item.childrenAnchorPointID);
            } else {
                childrenAnchorPoint = $('<div>');
                childrenAnchorPoint.addClass('children-anchor-point');
                childrenAnchorPoint.attr('id', item.id + '-children');
                itemDiv.append(childrenAnchorPoint);
            }

//            if(item.condition !== undefined) {
//                var inputSelector = itemDiv.find('input, select');
//
//                // hide initially if current value does not equal condition
//                if(inputSelector.val() !== item.condition) {
//                    childrenAnchorPoint.hide();
//                }
//
//                inputSelector.change(function(e) {
//                    if ($(this).val() === item.condition) {
//                        childrenAnchorPoint.slideDown('medium');
//                    } else {
//                        childrenAnchorPoint.slideUp('medium');
//                    }
//                });
//            }
            layoutChildren(item.children, data, childrenAnchorPoint, item.id);
        }

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

    function layoutChildren(children, data, childrenAnchorPointID, itemID) {
        $.each(children, function(index, child) {
            layoutItem(child, data, childrenAnchorPointID, itemID, index);
        });
    }

    return function(mainContainerSelector, formStructure, formData, postURL, csrfToken) {
        formStructure.postURL = postURL;
        formStructure.csrfToken = csrfToken;

        $.ajax({
            url: '/static/hdb_templates/application_preview.handlebars',
            success: function(data) {
                var template = Handlebars.compile(data);
                $(mainContainerSelector).append(template(formStructure));
            },
            async: false
        });

        layoutChildren(formStructure.children, formData, '#' + formStructure.childrenAnchorPointID, 'item', 0);

        var sectionList = $('#sectionList');
        $('body').scrollspy({ target: '#sectionList' });
        sectionList.affix({ offset: { top: 200 }});

    };
});