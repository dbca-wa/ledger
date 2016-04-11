define(['jQuery', 'handlebars.runtime', 'bootstrap', 'js/handlebars_helpers', 'js/precompiled_handlebars_templates'], function($, Handlebars) {
    function _layoutItem(item, index, isRepeat, itemDataCurrent, itemDataPrevious) {
        var itemContainer = $('<div>');

        if(item.type == 'section') {
            item.index = index;
        }

        // if this is a repeatable item (such as a group), add repetitionIndex to item ID
        if(item.isRepeatable) {
            item.isRemovable = isRepeat;
        }

        if(itemDataCurrent != undefined && item.name in itemDataCurrent) {
            item.valueCurrent = itemDataCurrent[item.name];
        }

        if(itemDataPrevious != undefined && item.name in itemDataPrevious) {
            item.valuePrevious = itemDataPrevious[item.name];
        }

        if(item.type === 'section' || item.type === 'group') {
            item.isPreviewMode = true;
            itemContainer.append(Handlebars.templates[item.type](item));
        } else if (item.type === 'radiobuttons' || item.type === 'select') {
            itemContainer.append($('<label>').text(item.label));
            $.each(item.options, function(index, option) {
                if(option.value === item.value) {
                    itemContainer.append($('<p>').text(option.label));
                }
            });
        } else {
            itemContainer.append($('<label>').text(item.label));

            if(item.valueCurrent === item.valuePrevious) { 
                itemContainer.append($('<p>').text(item.valueCurrent));
            } else {
                itemContainer.append($('<p>').addClass('current-data').text(item.valueCurrent));
                itemContainer.append($('<p>').addClass('previous-data').text(item.valuePrevious));
            }
        }

        // unset item value if they were set otherwise there may be unintended consequences if extra form fields are created dynamically
        item.valueCurrent = undefined;
        item.valuePrevious = undefined;

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
                    if(item.condition === undefined || item.condition === itemDataCurrent[item.name]) {
                        var childDataCurrent, childDataPrevious;

                        if(itemDataCurrent !== undefined) {
                            childDataCurrent = itemDataCurrent[child.name][0];
                        }

                        if(itemDataPrevious !== undefined) {
                            childDataPrevious = itemDataPrevious[child.name][0];
                        }

                        childrenAnchorPoint.append(_layoutItem(child, childIndex, false, childDataCurrent, childDataPrevious));
                    }

                    var repeatItemsAnchorPoint = $('<div>');
                    childrenAnchorPoint.append(repeatItemsAnchorPoint);

                    if(itemDataCurrent != undefined && child.name in itemDataCurrent && itemDataCurrent[child.name].length > 1) {
                        $.each(itemDataCurrent[child.name].slice(1), function(childRepetitionIndex, repeatData) {
                            repeatItemsAnchorPoint.append(_layoutItem(child, index, true, repeatData));
                        });
                    }
                } else {
                    // only show children items when the item has no condition or the condition is met
                    if(item.condition === undefined || item.condition === itemDataCurrent[item.name]) {
                        childrenAnchorPoint.append(_layoutItem(child, childIndex, false, itemDataCurrent, itemDataPrevious));
                    }
                }
            });
        }

        return itemContainer;
    }

    return {
        layoutPreviewItems: function(containerSelector, formStructure, currentData, previousData) {
            var container = $(containerSelector);

            $.each(formStructure, function(index, item) {
                container.append(_layoutItem(item, index, false, currentData, previousData));
            });
        }
    }
});