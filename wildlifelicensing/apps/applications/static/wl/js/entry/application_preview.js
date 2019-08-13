define(['jQuery', 'handlebars.runtime', 'bootstrap', 'js/handlebars_helpers', 'js/precompiled_handlebars_templates'], function($, Handlebars) {
    function _setupDisclaimers(disclaimersSelector, lodgeSelector) {
        var $disclaimers = $(disclaimersSelector),
            $lodge = $(lodgeSelector),
            $form = $lodge.parents('form'),
            $buttonClicked;

        if($lodge.hasClass('disabled')) {
            $lodge.tooltip({});
        }

        // ensure form only submits when either approve (enterConditions) is enabled or decline is clicked
        $(lodgeSelector).click(function() {
            $buttonClicked = $(this);
        });

        $form.submit(function(e) {
            if($buttonClicked.is($lodge) && $lodge.hasClass('disabled')) {
                e.preventDefault();
            }
        });

        // enable lodge button if the number of checked checkboxes is the same as the number of
        // checkboxes in the dislaimer div (which is the parent of the disclaimers selector's elements)
        $(disclaimersSelector).change(function(e) {
            if($(disclaimersSelector).parent().find(':checked').length === $(disclaimersSelector).length) {
                $lodge.removeClass('disabled');
                $lodge.tooltip('destroy');
            } else {
                $lodge.addClass('disabled');
                $lodge.tooltip({});
            }
        });
    }

    function _layoutItem(item, isRepeat, itemData) {
        var itemContainer = $('<div>'),
            childrenAnchorPoint;

        // if this is a repeatable item (such as a group), add repetitionIndex to item ID
        if(item.isRepeatable) {
            item.isRemovable = isRepeat;
        }

        if(itemData !== undefined && item.name in itemData) {
            item.value = itemData[item.name];
        } else {
            item.value = "";
        }

        if(item.type === 'section' || item.type === 'group') {
            item.isPreviewMode = true;
            itemContainer.append(Handlebars.templates[item.type](item));
            _initCollapsible(itemContainer);
        } else if (item.type === 'radiobuttons' || item.type === 'select') {
            var isSpecified = false;
            itemContainer.append($('<label>').text(item.label));
            $.each(item.options, function(index, option) {
                if(option.value === item.value) {
                    itemContainer.append($('<p>').text(option.label));
                    isSpecified = true;
                }
            });

            if(!isSpecified) {
                itemContainer.append($('<p>').text("Not specified"));
            }
        } else if(item.type === 'checkbox') {
            if(item.value) {
                itemContainer.append($('<p>').text(item.label));
            }
        } else if(item.type === 'declaration') {
            itemContainer.append($('<label>').text(item.label));
            itemContainer.append($('<p>').text(item.value ? 'Declaration checked' : 'Declaration not checked'));
        } else if(item.type === 'file') {
            itemContainer.append($('<label>').text(item.label));
            if(item.value) {
                var fileLink = $('<a>');
                fileLink.attr('href', item.value);
                fileLink.attr('target', '_blank');
                fileLink.text(item.value.substr(item.value.lastIndexOf('/') + 1));
                itemContainer.append($('<p>').append(fileLink));
            } else {
                itemContainer.append($('<p>').text("No file attached"));
            }
        } else if(item.type === 'label') {
            itemContainer.append($('<label>').text(item.label));
        } else {
            itemContainer.append($('<label>').text(item.label));
            if(item.value) {
                itemContainer.append($('<p>').text(item.value));
            } else {
                itemContainer.append($('<p>').text("Not specified"));
            }
        }

        // unset item value if they were set otherwise there may be unintended consequences if extra form fields are created dynamically
        item.value = undefined;

        childrenAnchorPoint = _getCreateChildrenAnchorPoint(itemContainer);

        if(item.conditions !== undefined) {
            if(item.conditions !== undefined) {
                $.each(item.conditions, function(condition, children) {
                    if(condition === itemData[item.name]) {
                        $.each(children, function(childIndex, child) {
                            _appendChild(child, childrenAnchorPoint, itemData);
                        });
                    }
                });
            }
        }

        if(item.children !== undefined) {
            $.each(item.children, function(childIndex, child) {
                _appendChild(child, childrenAnchorPoint, itemData);
            });
        }

        return itemContainer;
    }

    function _appendChild(child, childrenAnchorPoint, itemData) {
        if(child.isRepeatable) {
            var childData;
            if(itemData !== undefined) {
                childData = itemData[child.name][0];
            }
            childrenAnchorPoint.append(_layoutItem(child, false, childData));

            var repeatItemsAnchorPoint = $('<div>');
            childrenAnchorPoint.append(repeatItemsAnchorPoint);

            if(itemData !== undefined && child.name in itemData && itemData[child.name].length > 1) {
                $.each(itemData[child.name].slice(1), function(childRepetitionIndex, repeatData) {
                    repeatItemsAnchorPoint.append(_layoutItem(child, true, repeatData));
                });
            }
        } else {
            childrenAnchorPoint.append(_layoutItem(child, false, itemData));
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
        layoutPreviewItems: function(containerSelector, formStructure, data, tempFilesUrl) {
            var container = $(containerSelector);

            for(var i = 0; i < formStructure.length; i++) {
                var itemData;

                // ensure item data exists
                if(data && i < data.length) {
                    itemData = data[i][formStructure[i].name][0];
                }

                container.append(_layoutItem(formStructure[i], false, itemData));
            }
        },
        initialiseSidebarMenu: function(sidebarMenuSelector) {
            $('.section').each(function(index, value) {
                var link = $('<a>');
                link.attr('href', '#' + $(this).attr('id'));
                link.text($(this).text());
                $('#sectionList ul').append($('<li>').append(link));
            });

            var sectionList = $(sidebarMenuSelector);
            $('body').scrollspy({ target: '#sectionList' });
            sectionList.affix({ offset: { top: sectionList.offset().top }});
        },
        setupDisclaimer: _setupDisclaimers
    };
});
