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

        if(item.type === 'section' || item.type === 'group' || item.type === 'table') {
            item.isPreviewMode = true;
            var $template = $(Handlebars.templates[item.type](item));

            if(item.type === 'group' || item.type === 'table') {
                if(itemDataCurrent !== itemDataPrevious) {
                    if(itemDataPrevious === undefined && isRepeat) {
                        $template.addClass('current-data');
                    } else if (itemDataCurrent === undefined && isRepeat) {
                        $template.addClass('previous-data');
                    }
                }
            }

            itemContainer.append($template);
        } else if (item.type === 'radiobuttons' || item.type === 'select') {
            itemContainer.append($('<label>').text(item.label));
            if(item.valueCurrent === item.valuePrevious || (item.valuePrevious === undefined && isRepeat)) {
                var isSpecified = false;
                $.each(item.options, function(index, option) {
                    if(option.value === item.valueCurrent) {
                        itemContainer.append($('<p>').text(option.label));
                        isSpecified = true;
                    }
                });

                if(!isSpecified) {
                    itemContainer.append($('<p>').text("Not specified"));
                }
            } else {
                var labelCurrent, labelPrevious;
                $.each(item.options, function(index, option) {
                    if(option.value === item.valueCurrent) {
                        labelCurrent = $('<p>').addClass('current-data').text(option.label);
                    } else if (option.value === item.valuePrevious) {
                        labelPrevious = $('<p>').addClass('previous-data').text(option.label);
                    }
                });

                itemContainer.append(labelCurrent);
                itemContainer.append(labelPrevious);
            }
        } else if(item.type === 'checkbox') {
            if((item.valueCurrent === item.valuePrevious && item.valueCurrent) || (item.valuePrevious === undefined && isRepeat)) {
                itemContainer.append($('<p>').text(item.label));
            } else {
                if(item.valueCurrent) {
                    itemContainer.append($('<p>').text(item.label).addClass('current-data'));
                } else if (item.valuePrevious){
                    itemContainer.append($('<p>').text(item.label).addClass('previous-data'));
                }
            }
        } else if(item.type === 'declaration') {
            itemContainer.append($('<label>').text(item.label));

            if(item.valueCurrent === item.valuePrevious || (item.valuePrevious === undefined && isRepeat)) {
                itemContainer.append($('<p>').text(item.valueCurrent ? 'Declaration checked' : 'Declaration not checked'));
            } else {
                itemContainer.append($('<p>').addClass('current-data').text(item.valueCurrent ? 'Declaration checked' : 'Declaration not checked'));
                itemContainer.append($('<p>').addClass('previous-data').text(item.valuePrevious ? 'Declaration checked' : 'Declaration not checked'));
            }
        } else if(item.type === 'file') {
            itemContainer.append($('<label>').text(item.label));

            if(item.valueCurrent === item.valuePrevious || (item.valuePrevious === undefined && isRepeat)) {
                if(item.valueCurrent) {
                    var fileLink = $('<a>');
                    fileLink.attr('href', item.valueCurrent);
                    fileLink.attr('target', '_blank');
                    fileLink.text(item.valueCurrent.substr(item.valueCurrent.lastIndexOf('/') + 1));
                    itemContainer.append($('<p>').append(fileLink));
                } else {
                    itemContainer.append($('<p>').text("No file attached"));
                }
            } else {
                var currentFileLink = $('<a>'),
                    previousFileLink = $('<a>');

                currentFileLink.attr('href', item.valueCurrent);
                currentFileLink.attr('target', '_blank');
                currentFileLink.text(item.value.substr(item.valueCurrent.lastIndexOf('/') + 1));

                previousFileLink.attr('href', item.valueCurrent);
                previousFileLink.attr('target', '_blank');
                previousFileLink.text(item.value.substr(item.valuePrevious.lastIndexOf('/') + 1));

                itemContainer.append(currentFileLink).addClass('current-data');
                itemContainer.append(previousFileLink).addClass('previous-data');
            }
        } else {
            itemContainer.append($('<label>').text(item.label));

            if(item.valueCurrent === item.valuePrevious || (item.valuePrevious === undefined && isRepeat)) {
                itemContainer.append($('<p>').text(item.valueCurrent));
            } else {
                itemContainer.append($('<p>').addClass('current-data').text(item.valueCurrent));
                itemContainer.append($('<p>').addClass('previous-data').text(item.valuePrevious));
            }
        }

        // unset item value if they were set otherwise there may be unintended consequences if extra form fields are created dynamically
        item.valueCurrent = undefined;
        item.valuePrevious = undefined;

        if(item.conditions !== undefined) {
            var childrenAnchorPoint = _getCreateChildrenAnchorPoint(itemContainer);

            if(item.conditions !== undefined) {
                $.each(item.conditions, function(condition, children) {
                    if(condition === itemDataCurrent[item.name]) {
                        $.each(children, function(childIndex, child) {
                            childrenAnchorPoint.append(_layoutItem(child, childIndex, isRepeat, itemDataCurrent, itemDataPrevious));
                        });
                    }
                });
            }
        }

        if(item.children !== undefined) {
            if(item.type !== "table") {
                var childrenAnchorPoint = _getCreateChildrenAnchorPoint(itemContainer);

                $.each(item.children, function(childIndex, child) {
                    if(child.isRepeatable) {
                        var childDataCurrent, childDataPrevious;

                        if(itemDataCurrent !== undefined) {
                            childDataCurrent = itemDataCurrent[child.name][0];
                        }

                        if(itemDataPrevious !== undefined) {
                            childDataPrevious = itemDataPrevious[child.name][0];
                        }

                        childrenAnchorPoint.append(_layoutItem(child, childIndex, isRepeat, childDataCurrent, childDataPrevious));

                        var repeatItemsAnchorPoint = $('<div>');
                        childrenAnchorPoint.append(repeatItemsAnchorPoint);

                        if((itemDataCurrent != undefined && child.name in itemDataCurrent && itemDataCurrent[child.name].length > 1) ||
                                (itemDataPrevious != undefined && child.name in itemDataPrevious && itemDataPrevious[child.name].length > 1)) {
                            var itemDataLength;
                            if(itemDataCurrent[child.name] !== undefined && itemDataPrevious[child.name].length) {
                                itemDataLength = Math.max(itemDataCurrent[child.name].length, itemDataPrevious[child.name].length);
                            } else if (itemDataCurrent[child.name] !== undefined) {
                                itemDataLength = itemDataCurrent[child.name].length;
                            } else if (itemDataPrevious[child.name] !== undefined) {
                                itemDataLength = itemDataPrevious[child.name].length;
                            } 
    
                            for(var i=1; i<itemDataLength; i++) {
                                repeatItemsAnchorPoint.append(_layoutItem(child, index, true, itemDataCurrent[child.name][i], itemDataPrevious[child.name][i]));
                            }
                        }
                    } else {
                        childrenAnchorPoint.append(_layoutItem(child, childIndex, isRepeat, itemDataCurrent, itemDataPrevious));
                    }
                });
            } else {
                var $table = itemContainer.find('table');

                if(itemDataCurrent !== undefined && itemDataCurrent[item.name]) {
                    for(var i = 0; i < Math.max(itemDataCurrent[item.name].length, itemDataPrevious[item.name].length); i++) {
                        _createTableRow(item, $table, itemDataCurrent[item.name][i], itemDataPrevious[item.name][i]);
                    };
                } else {
                    // make sure there is at least one blank road
                    _createTableRow(item, $table);
                }

                itemContainer.find('.add-group').find('a').click(function() {
                    _createTableRow(item, $table, itemData);
                });
            }
        }

        return itemContainer;
    }

    function _getCreateChildrenAnchorPoint($itemContainer) {
        var $childrenAnchorPoint;

        // if no children anchor point was defined within the template, create one under current item
        if($itemContainer.find('.children-anchor-point').length) {
            $childrenAnchorPoint = $itemContainer.find('.children-anchor-point');
        } else {
            $childrenAnchorPoint = $('<div>');
            $childrenAnchorPoint.addClass('children-anchor-point');
            $itemContainer.append($childrenAnchorPoint);
        }

        return $childrenAnchorPoint;
    }

    function _createTableRow(item, $table, itemDataCurrent, itemDataPrevious) {
        var $row = $('<tr>');

        $.each(item.children, function(index, child) {
            var $col = $('<td>');
            $col.append(_layoutItem(child, index, false, itemDataCurrent, itemDataPrevious));
            $col.find('label:first').remove();
            $row.append($col);
        });

        $table.append($row);
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