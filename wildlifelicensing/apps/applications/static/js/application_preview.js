define(['jQuery', 'handlebars', 'bootstrap'], function($, Handlebars) {
    var templates = {};

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

        if(item.type === 'section' || item.type === 'group') {
            itemDiv.append(getTemplate(item.type)(item));
        } else if (item.type === 'radiobuttons' || item.type === 'select') {
            itemDiv.append($('<label>').text(item.label));
            $.each(item.options, function(index, option) {
                if(option.value === data[item.name]) {
                    itemDiv.append($('<p>').text(option.label));
                }
            });
        } 
        else {
            itemDiv.append($('<label>').text(item.label));
            itemDiv.append($('<p>').text(data[item.name]));
        }

        if(item.children !== undefined) {
            var childrenAnchorPoint;

            // get child anchor point selector and if no children anchor point was defined in the 
            // template, create one under current item
            if($('#' + item.childrenAnchorPointID).length) {
                childrenAnchorPoint = $('#' + item.childrenAnchorPointID);
            } else {
                childrenAnchorPoint = $('<div>');
                childrenAnchorPoint.addClass('children-anchor-point');
                childrenAnchorPoint.attr('id', item.id + '-children');
                itemDiv.append(childrenAnchorPoint);
            }

            // only show children items when the item has no condition or the condition is met
            if(item.condition === undefined || item.condition === data[item.name]) {
                layoutChildren(item.children, data, childrenAnchorPoint, item.id);
            }
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

    return function(mainContainerSelector, formStructure, formData, csrfToken) {
        formStructure.csrfToken = csrfToken;
        $(mainContainerSelector).append(getTemplate('application_preview')(formStructure));

        layoutChildren(formStructure.children, formData, '#' + formStructure.childrenAnchorPointID, 'item', 0);

        var sectionList = $('#sectionList');
        $('body').scrollspy({ target: '#sectionList' });
        sectionList.affix({ offset: { top: 200 }});

    };
});