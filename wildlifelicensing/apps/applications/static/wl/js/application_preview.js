define(['jQuery', 'handlebars', 'bootstrap', 'js/handlebars_helpers'], function($, Handlebars) {
    var templates = {};

    function _getTemplate(templateName) {
        if (templates[templateName] === undefined) {
            $.ajax({
                url: '/static/wl/hdb_templates/' + templateName + '.handlebars',
                success: function(data) {
                    templates[templateName] = Handlebars.compile(data);
                },
                async: false
            });
        }

        return templates[templateName]
    }

    function _layoutItem(item, index, isRepeat, itemData) {
        var itemContainer = $('<div>');

        if(item.type == 'section') {
            item.index = index;
        }

        // if this is a repeatable item (such as a group), add repetitionIndex to item ID
        if(item.isRepeatable) {
            item.isRemovable = isRepeat;
        }

        if(itemData != undefined && item.name in itemData) {
            item.value = itemData[item.name];
        }

        if(item.type === 'section' || item.type === 'group') {
            item.isPreviewMode = true;
            itemContainer.append(_getTemplate(item.type)(item));
        } else if (item.type === 'radiobuttons' || item.type === 'select') {
            itemContainer.append($('<label>').text(item.label));
            $.each(item.options, function(index, option) {
                if(option.value === item.value) {
                    itemContainer.append($('<p>').text(option.label));
                }
            });
        } else {
            itemContainer.append($('<label>').text(item.label));
            itemContainer.append($('<p>').text(item.value));
        }

        // unset item value if they were set otherwise there may be unintended consequences if extra form fields are created dynamically
        item.value = undefined;

        if(item.children !== undefined) {
            var childrenAnchorPoint;

            // if no children anchor point was defined within the template, create one under current item
            if(itemContainer.find('.children-anchor-point').length) {
                childrenAnchorPoint = itemContainer.find('.children-anchor-point');
            } else {
                childrenAnchorPoint = $('<div>');
                childrenAnchorPoint.addClass('children-anchor-point');
                itemContainer.append(childrenAnchorPoint);
            }

            $.each(item.children, function(childIndex, child) {
                if(child.isRepeatable) {
                    // only show children items when the item has no condition or the condition is met
                    if(item.condition === undefined || item.condition === itemData[item.name]) {
                        var childData;
                        if(itemData !== undefined) {
                            childData = itemData[child.name][0];
                        }
                        childrenAnchorPoint.append(_layoutItem(child, childIndex, false, childData));
                    }

                    var repeatItemsAnchorPoint = $('<div>');
                    childrenAnchorPoint.append(repeatItemsAnchorPoint);

                    if(itemData != undefined && child.name in itemData && itemData[child.name].length > 1) {
                        $.each(itemData[child.name].slice(1), function(childRepetitionIndex, repeatData) {
                            repeatItemsAnchorPoint.append(_layoutItem(child, index, true, repeatData));
                        });
                    }
                } else {
                    // only show children items when the item has no condition or the condition is met
                    if(item.condition === undefined || item.condition === itemData[item.name]) {
                        childrenAnchorPoint.append(_layoutItem(child, childIndex, false, itemData));
                    }
                }
            });
        }

        // if item is a section, need to add to side menu list
        if(item.type === 'section') {
            var link = $('<a>');
            link.attr('href', '#section-' + index);
            link.text(item.label);
            $('#sectionList ul').append($('<li>').append(link));
        }

        return itemContainer;
    }

    return {
        layoutPreviewItems: function(formContainerSelector, formStructure, data) {
            var formContainer = $(formContainerSelector);

            $.each(formStructure, function(index, child) {
                formContainer.append(_layoutItem(child, index, false, data));
            });
        },
        initialiseSidebarMenu(sidebarMenuSelector) {
            var sectionList = $(sidebarMenuSelector);
            $('body').scrollspy({ target: '#sectionList' });
            sectionList.affix({ offset: { top: sectionList.offset().top }});
        }
    }
});