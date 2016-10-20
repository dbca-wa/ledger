define(['jQuery', 'handlebars.runtime', 'bootstrap', 'js/handlebars_helpers', 'js/precompiled_handlebars_templates'], function($, Handlebars) {
    function _layoutItem(item, isRepeat, itemDataCurrent, itemDataPrevious) {
        var itemContainer = $('<div>'),
            childrenAnchorPoint;

        // if this is a repeatable item (such as a group), add repetitionIndex to item ID
        if(item.isRepeatable) {
            item.isRemovable = isRepeat;
        }

        if(itemDataCurrent !== undefined && item.name in itemDataCurrent) {
            item.valueCurrent = itemDataCurrent[item.name];
        }

        if(itemDataPrevious !== undefined && item.name in itemDataPrevious) {
            item.valuePrevious = itemDataPrevious[item.name];
        }

        if(item.type === 'section' || item.type === 'group') {
            item.isPreviewMode = true;
            var $template = $(Handlebars.templates[item.type](item));

            if(item.type === 'group') {
                if(itemDataCurrent !== itemDataPrevious) {
                    if(itemDataPrevious === undefined && isRepeat) {
                        $template.addClass('current-data');
                    } else if (itemDataCurrent === undefined && isRepeat) {
                        $template.addClass('previous-data');
                    }
                }
            }

            itemContainer.append($template);

            _initCollapsible(itemContainer);
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
            var currentFileLink = $('<a>'),
                previousFileLink = $('<a>');

            itemContainer.append($('<label>').text(item.label));

            if(item.valueCurrent === item.valuePrevious || (item.valuePrevious === undefined && isRepeat)) {
                if(item.valueCurrent) {
                    currentFileLink.attr('href', item.valueCurrent);
                    currentFileLink.attr('target', '_blank');
                    currentFileLink.text(item.valueCurrent.substr(item.valueCurrent.lastIndexOf('/') + 1));
                    itemContainer.append($('<p>').append(currentFileLink));
                } else {
                    itemContainer.append($('<p>').text("No file attached"));
                }
            } else {
                if (item.valueCurrent && item.valuePrevious) {
                    currentFileLink.attr('href', item.valueCurrent);
                    currentFileLink.attr('target', '_blank');
                    currentFileLink.text(item.valueCurrent.substr(item.valueCurrent.lastIndexOf('/') + 1));
                    currentFileLink.addClass('current-data');

                    previousFileLink.attr('href', item.valuePrevious);
                    previousFileLink.attr('target', '_blank');
                    previousFileLink.text(item.valuePrevious.substr(item.valuePrevious.lastIndexOf('/') + 1));
                    previousFileLink.addClass('previous-data');

                    itemContainer.append($('<p>').append(currentFileLink));
                    itemContainer.append($('<p>').append(previousFileLink).addClass('previous-data'));
                } else if (item.valueCurrent && !item.valuePrevious) {
                    currentFileLink.attr('href', item.valueCurrent);
                    currentFileLink.attr('target', '_blank');
                    currentFileLink.text(item.valueCurrent.substr(item.valueCurrent.lastIndexOf('/') + 1));
                    currentFileLink.addClass('current-data');

                    itemContainer.append($('<p>').append(currentFileLink));
                    itemContainer.append($('<p>').addClass('previous-data').text("Not specified"));
                } else if (!item.valueCurrent && item.valuePrevious) {
                    previousFileLink.attr('href', item.valuePrevious);
                    previousFileLink.attr('target', '_blank');
                    previousFileLink.text(item.valuePrevious.substr(item.valuePrevious.lastIndexOf('/') + 1));
                    previousFileLink.addClass('previous-data');

                    itemContainer.append($('<p>').addClass('current-data').text("Not specified"));
                    itemContainer.append($('<p>').append(previousFileLink));
                }
            }
        } else if (item.type == 'label') {
            itemContainer.append($('<label>').text(item.label));
        } else {
            itemContainer.append($('<label>').text(item.label));

            if(item.valueCurrent === item.valuePrevious || (item.valuePrevious === undefined && isRepeat)) {
                if(item.valueCurrent) {
                    itemContainer.append($('<p>').text(item.valueCurrent));
                } else {
                    itemContainer.append($('<p>').text("Not specified"));
                }
            } else {
                itemContainer.append($('<p>').addClass('current-data').text(item.valueCurrent));
                itemContainer.append($('<p>').addClass('previous-data').text(item.valuePrevious));
            }
        }

        // unset item value if they were set otherwise there may be unintended consequences if extra form fields are created dynamically
        item.valueCurrent = undefined;
        item.valuePrevious = undefined;

        childrenAnchorPoint = _getCreateChildrenAnchorPoint(itemContainer);

        if(item.conditions !== undefined) {
            if(item.conditions !== undefined) {
                $.each(item.conditions, function(condition, children) {
                    if(condition === itemDataCurrent[item.name]) {
                        $.each(children, function(childIndex, child) {
                            _appendChild(child, childrenAnchorPoint, itemDataCurrent, itemDataPrevious);
                        });
                    }
                });
            }
        }

        if(item.children !== undefined) {
            $.each(item.children, function(childIndex, child) {
                _appendChild(child, childrenAnchorPoint, itemDataCurrent, itemDataPrevious);
            });
        }
        return itemContainer;
    }

    function _appendChild(child, childrenAnchorPoint, itemDataCurrent, itemDataPrevious) {
        if(child.isRepeatable) {
            var childDataCurrent, childDataPrevious,
            	repeatItemsAnchorPoint = $('<div>');

            if(itemDataCurrent !== undefined) {
                childDataCurrent = itemDataCurrent[child.name][0];
            }

            if(itemDataPrevious !== undefined) {
                childDataPrevious = itemDataPrevious[child.name][0];
            }

            childrenAnchorPoint.append(_layoutItem(child, false, childDataCurrent, childDataPrevious));
            
            childrenAnchorPoint.append(repeatItemsAnchorPoint);

            if((itemDataCurrent !== undefined && child.name in itemDataCurrent && itemDataCurrent[child.name].length > 1) ||
                    (itemDataPrevious !== undefined && child.name in itemDataPrevious && itemDataPrevious[child.name].length > 1)) {
                var itemDataLength;
                if(itemDataCurrent[child.name] !== undefined && itemDataPrevious[child.name].length) {
                    itemDataLength = Math.max(itemDataCurrent[child.name].length, itemDataPrevious[child.name].length);
                } else if (itemDataCurrent[child.name] !== undefined) {
                    itemDataLength = itemDataCurrent[child.name].length;
                } else if (itemDataPrevious[child.name] !== undefined) {
                    itemDataLength = itemDataPrevious[child.name].length;
                }

                for(var i=1; i<itemDataLength; i++) {
                    repeatItemsAnchorPoint.append(_layoutItem(child, true, itemDataCurrent[child.name][i], itemDataPrevious[child.name][i]));
                }
            }
        } else {
            childrenAnchorPoint.append(_layoutItem(child, false, itemDataCurrent, itemDataPrevious));
        }
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

    function _initCollapsible($itemContainer) {
        var $collapsible = $itemContainer.find('.children-anchor-point').first(),
            $topLink = $collapsible.siblings('.collapse-link-top'),
            $topLinkSpan = $topLink.find('span'),
            $bottomLink = $collapsible.siblings('.collapse-link-bottom').first();

        $collapsible.on('hide.bs.collapse', function () {
            $topLinkSpan.removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');
            if($bottomLink.length) {
                $bottomLink.hide();
            }
        }).on('show.bs.collapse', function() {
            $topLinkSpan.removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
        }).on('shown.bs.collapse', function() {
            if($bottomLink.length) {
                $bottomLink.show();
            };
        });

        $topLink.click(function() {
            $collapsible.collapse('toggle');
        });

        if($bottomLink.length) {
            $bottomLink.click(function() {
                $collapsible.collapse('toggle');
            });
        }
    }

    return {
        layoutPreviewItems: function(containerSelector, formStructure, currentData, previousData) {
            var container = $(containerSelector);

            for(var i = 0; i < formStructure.length; i++) {
                var currentItemData,
                    previousItemData;

                // ensure item data exists
                if(currentData && i < currentData.length) {
                    currentItemData = currentData[i][formStructure[i].name][0];
                }

                if(previousData && i < previousData.length) {
                    previousItemData = previousData[i][formStructure[i].name][0];
                }

                container.append(_layoutItem(formStructure[i], false, currentItemData, previousItemData));
            }
        }
    };
});
