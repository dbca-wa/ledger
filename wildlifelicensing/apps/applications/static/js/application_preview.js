define(['jQuery', 'handlebars', 'bootstrap'], function($, Handlebars) {
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

        $(parentAnchorPointSelector).append(itemDiv);

        // if this is a repeatable item (such as a group), add repetitionIndex to item ID
        if(item.isRepeatable) {
            repetitionIndex = repetitionIndex !== undefined ? repetitionIndex: 0;
            item.id += '-repeat-' + repetitionIndex;
        }

        item.childrenAnchorPointID = item.id + '-children';


        var data = item.name in applicationData ? applicationData[item.name] : item.data;

        if(item.type === 'section') {
            itemDiv.append(getTemplate(item.type)(item));
        } else if(item.type === 'group') {
            // need to save this state as is unset because we don't want copy link in template being rendered
            var isItemRepeatable = item.isRepeatable;
            item.isRepeatable = false;
            itemDiv.append(getTemplate(item.type)(item));
            item.isRepeatable = isItemRepeatable;

            repetitionIndex = repetitionIndex !== undefined ? repetitionIndex: 0;

            // if the repetitionIndex is less than the amount of data in the array of objects for this group, set the data value of each child element
            if(repetitionIndex < data.length) {
                $.each(item.children, function(index, child) {
                    child.data = data[repetitionIndex][child.name];
                });
            }
        } else if (item.type === 'radiobuttons' || item.type === 'select') {
            itemDiv.append($('<label>').text(item.label));
            $.each(item.options, function(index, option) {
                if(option.value === data) {
                    itemDiv.append($('<p>').text(option.label));
                }
            });
        } 
        else {
            itemDiv.append($('<label>').text(item.label));
            itemDiv.append($('<p>').text(data));
        }

        // unset item data
        item.data = undefined;

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
            if(item.condition === undefined || item.condition === applicationData[item.name]) {
                layoutChildren(item.children, childrenAnchorPoint, item.id);
            }
        }

        if(item.type === 'section') {
            var link = $('<a>');
            link.attr('href', '#' + item.id);
            link.text(item.label);
            $('#sectionList ul').append($('<li>').append(link));
        } else if(item.type === 'group' && item.isRepeatable) {
            if(repetitionIndex === 0) {
                var repeatItemsAnchorPoint = $('<div>').attr('id', item.name + '-repeated-items');
                itemDiv.after(repeatItemsAnchorPoint);
            }

            if(repeatItemsAnchorPoint === undefined) {
                repeatItemsAnchorPoint = $('#'+ item.name + "-repeated-items")
            }

            if(applicationData != undefined && item.name in applicationData && repetitionIndex < applicationData[item.name].length - 1) {
                layoutItem(item, repeatItemsAnchorPoint, parentItemID, index, ++repetitionIndex);
            }
        }
    }

    function layoutChildren(children, childrenAnchorPointID, itemID) {
        $.each(children, function(index, child) {
            layoutItem(child, childrenAnchorPointID, itemID, index);
        });
    }

    return function(mainContainerSelector, formStructure, formData, csrfToken) {
        applicationData = formData;
        formStructure.csrfToken = csrfToken;
        $(mainContainerSelector).append(getTemplate('application_preview')(formStructure));

        layoutChildren(formStructure.children, '#' + formStructure.childrenAnchorPointID, 'item', 0);

        var sectionList = $('#sectionList');
        $('body').scrollspy({ target: '#sectionList' });
        sectionList.affix({ offset: { top: 200 }});

    };
});