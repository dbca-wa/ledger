define(['jQuery', 'handlebars.runtime', 'parsley', 'bootstrap', 'bootstrap-datetimepicker', 'bootstrap-3-typeahead',
        'js/handlebars_helpers', 'js/precompiled_handlebars_templates'], function($, Handlebars) {
    function _layoutItem(item, repetition, suffix, itemData) {
        var $itemContainer = $('<div>'),
            $childrenAnchorPoint;

        item.isRemovable = repetition > 0;

        if(itemData !== undefined && item.name in itemData) {
            item.value = itemData[item.name];
        }

        item.name += suffix + '-' + repetition;

        $itemContainer.append(Handlebars.templates[item.type](item));

        _initInputField(item, $itemContainer);

        if(item.type === 'section' || item.type === 'group') {
            _initCollapsible($itemContainer);
        }

        // unset item name and value if they were set otherwise there may be unintended consequences if extra form fields are created dynamically
        item.name = item.name.slice(0, item.name.indexOf(suffix));
        item.value = undefined;

        $childrenAnchorPoint = _getCreateChildrenAnchorPoint($itemContainer);

        if(item.conditions !== undefined) {
            var $input = $itemContainer.find('input, select, textarea'),
                initialInputValue = _getInputValue(item, $input);

            // show/hide conditional children initially depending on input's initial value
            if(initialInputValue in item.conditions) {
                var $conditionalChildren = $('<div>');
                $conditionalChildren.attr('id', initialInputValue);
                $.each(item.conditions[initialInputValue], function(childIndex, child) {
                    _appendChild(child, $conditionalChildren, 0, suffix, itemData);
                });
                $childrenAnchorPoint.append($conditionalChildren);
            }

            $input.change(function(e) {
                var inputValue = _getInputValue(item, $(this)),
                    $internalChildrenAnchorPoint = _getInputChildrenAnchorPoint($(this)),
                    $conditionalChildren,
                    $slideUpPromise;

                // hide any currently shown conditional children
                $slideUpPromise = $internalChildrenAnchorPoint.children().slideUp('medium').promise();

                if(inputValue in item.conditions) {
                    // get conditional child anchor point if it exists, else create it
                    $conditionalChildren = $internalChildrenAnchorPoint.find('#' + inputValue);

                    if($conditionalChildren.length === 0) {
                        $conditionalChildren = $('<div>');
                        $conditionalChildren.attr('id', inputValue);
                        $conditionalChildren.css('display', 'none');
                        $.each(item.conditions[inputValue], function(childIndex, child) {
                            _appendChild(child, $conditionalChildren, 0, suffix, itemData);
                        });
                        $internalChildrenAnchorPoint.append($conditionalChildren);
                    }

                    $slideUpPromise.done(function() {
                        $conditionalChildren.slideDown('medium');
                    });
                }
            });
        }

        if (item.children !== undefined) {
            // append all children to item
            $.each(item.children, function(childIndex, child) {
                _appendChild(child, $childrenAnchorPoint, 0, suffix + '-' + repetition, itemData);
            });
        }

        if(item.isRepeatable) {
            _setupRemoveEvents(item, $itemContainer, suffix);
        }

        return $itemContainer;
    }

    function _appendChild(child, $childrenAnchorPoint, repetition, suffix, itemData) {
        if(child.isRepeatable) {
            var childData;

            if(itemData !== undefined) {
                childData = itemData[child.name][0];
            }
            $childrenAnchorPoint.append(_layoutItem(child, repetition, suffix, childData));

            var repeatItemsAnchorPoint = $('<div>');
            $childrenAnchorPoint.append(repeatItemsAnchorPoint);

            var addGroupDiv = $('<div>').addClass('add-group');
            var addGroupLink = $('<a>').text('Add ' + child.label, itemData);

            var groupInput = $('<input>').attr('name', child.name + suffix + '-' + repetition).attr('type', 'hidden').val(1);

            addGroupDiv.append(groupInput);

            // closure to make sure repetition keeps incrementing each time add is clicked
            addGroupLink.click(function() {
                var groupCount = parseInt(groupInput.val()),
                    repeatItem = _layoutItem(child, groupCount, suffix);

                repeatItem.find('.hidden').removeClass('hidden');
                repeatItemsAnchorPoint.append(repeatItem);
                groupInput.val(groupCount + 1);
            });

            $childrenAnchorPoint.append(addGroupDiv.append(addGroupLink));

            if(itemData !== undefined && child.name in itemData && itemData[child.name].length > 1) {
                $.each(itemData[child.name].slice(1), function(childRepetitionIndex, repeatData) {
                    repeatItemsAnchorPoint.append(_layoutItem(child, childRepetitionIndex + 1, suffix, repeatData));
                    groupInput.val(parseInt(groupInput.val()) + 1);
                });
            }
        } else {
            $childrenAnchorPoint.append(_layoutItem(child, repetition, suffix, itemData));
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

    function _getInputChildrenAnchorPoint($input) {
        if($input.siblings('.children-anchor-point').length > 0) {
            return $input.siblings('.children-anchor-point');
        }

        if($input.parent().length > 0) {
            return _getInputChildrenAnchorPoint($input.parent());
        } else {
            return null;
        }
    }

    function _initInputField(item, $itemContainer) {
        if(item.type === 'species') {
            var species_type_arg = '';
            if(item.speciesType !== undefined) {
                species_type_arg = '&type=' + item.speciesType; 
            }

            // initialise species typeahead
            $itemContainer.find('.species').typeahead({
                minLength: 3,
                items: 'all',
                source: function (query, process) {
                    return $.get('/taxonomy/species_name?search=' + query + species_type_arg, function (data) {
                        return process(data);
                    });
                }
            });
        } else if(item.type === 'date') {
            // initialise datapickers
            $itemContainer.find('.date').datetimepicker({
                format: 'DD/MM/YYYY'
            });
        }
    }

    function _getInputValue(item, $input) {
        if(item.type === 'radiobuttons') {
            var checkedRadiobuttonValue = '';
            $input.each(function(index, radiobutton) {
                if ($(radiobutton).is(':checked')) {
                    checkedRadiobuttonValue = $(radiobutton).val();
                }
            });
            return checkedRadiobuttonValue;
        } else if (item.type === 'checkbox') {
            return $input.is(':checked') ? 'on': '';
        } else {
            return $input.val();
        }
    }

    function _initCollapsible($itemContainer, removeExistingEvents) {
        var $collapsible = $itemContainer.find('.children-anchor-point').first(),
            $topLink = $collapsible.siblings('.collapse-link-top'),
            $topLinkSpan = $topLink.find('span'),
            $bottomLink = $collapsible.siblings('.collapse-link-bottom').first();

        if(removeExistingEvents) {
            $collapsible.off('hide.bs.collapse').off('show.bs.collapse').off('shown.bs.collapse');
            $topLink.off('click');
            if($bottomLink.length) {
                $bottomLink.off('click');
            }
        }

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

    function _setupRemoveEvents(item, itemSelector, suffix) {
        itemSelector.find('[id^="remove_' + item.name + '"]').off('click').click(function(e) {
            var groupInput = $('[name^="' + item.name + suffix + '"]');
            itemSelector.remove();
            groupInput.val(parseInt(groupInput.val()) - 1);
        });

        // initialise all datapickers
        itemSelector.find('.date').datetimepicker({
            format: 'DD/MM/YYYY'
        });
    }

    return {
        layoutFormItems: function(formContainerSelector, formStructure, data) {
            var formContainer = $(formContainerSelector);

            for(var i = 0; i < formStructure.length; i++) {
                var itemData;

                // ensure item data exists
                if(data && i < data.length) {
                    itemData = data[i][formStructure[i].name][0];
                }

                formContainer.append(_layoutItem(formStructure[i], 0, '', itemData));
            }

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
        }
    };
});
