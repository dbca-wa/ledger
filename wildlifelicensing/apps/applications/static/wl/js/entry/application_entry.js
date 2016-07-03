define(['jQuery', 'handlebars.runtime', 'parsley', 'bootstrap', 'bootstrap-datetimepicker',
        'js/handlebars_helpers', 'js/precompiled_handlebars_templates'], function($, Handlebars) {
    function _layoutItem(item, repetition, suffix, itemData) {
        var $itemContainer = $('<div>');

        item.isRemovable = repetition > 0;

        if(itemData != undefined && item.name in itemData) {
            item.value = itemData[item.name];
        }

        suffix += '-' + repetition;

        item.name += suffix;

        $itemContainer.append(Handlebars.templates[item.type](item));

        // unset item name and value if they were set otherwise there may be unintended consequences if extra form fields are created dynamically
        item.name = item.name.slice(0, item.name.indexOf(suffix));
        item.value = undefined;

        if(item.conditions !== undefined) {
            var $childrenAnchorPoint = _getCreateChildrenAnchorPoint($itemContainer);

            if(item.conditions !== undefined) {
                var $input = $itemContainer.find('input, select'),
                    initialInputValue = _getInputValue(item, $input);

                // show/hide conditional children initially depending on input's initial value
                if(initialInputValue in item.conditions) {
                    var $conditionalChildren = $('<div>');
                    $conditionalChildren.attr('id', initialInputValue);
                    $.each(item.conditions[initialInputValue], function(childIndex, child) {
                        _appendChild(child, $conditionalChildren, repetition, suffix, itemData);
                    });
                    $childrenAnchorPoint.append($conditionalChildren);
                }

                $input.change(function(e) {
                    var inputValue = _getInputValue(item, $(this)),
                        $conditionalChildren,
                        $slideUpPromise;

                    // hide any currently shown conditional children
                    $slideUpPromise = $childrenAnchorPoint.children().slideUp('medium').promise();

                    if(inputValue in item.conditions) {
                        // get conditional child anchor point if it exists, else create it
                        $conditionalChildren = $childrenAnchorPoint.find('#' + inputValue);

                        if($conditionalChildren.length === 0) {
                            $conditionalChildren = $('<div>');
                            $conditionalChildren.attr('id', inputValue);
                            $conditionalChildren.css('display', 'none');
                            $.each(item.conditions[inputValue], function(childIndex, child) {
                                _appendChild(child, $conditionalChildren, repetition, suffix, itemData);
                            });
                            $childrenAnchorPoint.append($conditionalChildren);
                        }

                        $slideUpPromise.done(function() {
                            $conditionalChildren.slideDown('medium');
                        });
                    }
                });
            }
        }

        if (item.children !== undefined) {
            if(item.type !== "table") {
                var $childrenAnchorPoint = _getCreateChildrenAnchorPoint($itemContainer);

                // append all children to item
                $.each(item.children, function(childIndex, child) {
                    _appendChild(child, $childrenAnchorPoint, repetition, suffix, itemData);
                });
            } else {
                var $table = $itemContainer.find('table');

                if(itemData !== undefined && itemData[item.name]) {
                    $.each(itemData[item.name], function(childDataIndex, childData) {
                        _createTableRow(item, $table, childData);
                    });
                } else {
                    // make sure there is at least one blank road
                    _createTableRow(item, $table);
                }

                $itemContainer.find('.add-group').find('a').click(function() {
                    _createTableRow(item, $table, itemData);
                });
            }
        }

        if(item.isRepeatable) {
            _setupCopyRemoveEvents(item, $itemContainer, repetition, suffix);
        }

        return $itemContainer;
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

    function _createTableRow(item, $table, itemData) {
        var $row = $('<tr>');

        $.each(item.children, function(index, child) {
            var $col = $('<td>');
            _appendChild(index, child, $col, itemData);
            $col.find('label:first').remove();
            $row.append($col);
        });

        $row.append($('<td>').append($('<a>').text('Remove').click(function() {
            $row.remove();
        })));

        $table.append($row);
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

            // closure to make sure repetition keeps incrementing each time add is clicked
            addGroupLink.click((function(){
                var rep = repetition;

                return function() {
                    rep += 1;
                    repeatItem = _layoutItem(child, rep, suffix, itemData);
                    repeatItem.find('.hidden').removeClass('hidden');
                    repeatItemsAnchorPoint.append(repeatItem);
                };
            })());

            $childrenAnchorPoint.append(addGroupDiv.append(addGroupLink));

            if(itemData != undefined && child.name in itemData && itemData[child.name].length > 1) {
                $.each(itemData[child.name].slice(1), function(childRepetitionIndex, repeatData) {
                    repeatItemsAnchorPoint.append(_layoutItem(child, repetition, suffix, repeatData));
                });
            }
        } else {
            $childrenAnchorPoint.append(_layoutItem(child, repetition, suffix, itemData));
        }
    }

    function _getInputValue(item, $input) {
        if(item.type === 'radiobuttons') {
            return  $input.is(':checked') ? $input.val(): '';
        } else if (item.type === 'checkbox') {
            return $input.is(':checked') ? 'on': '';
        } else {
            return $input.val();
        }
    }

    function _setupCopyRemoveEvents(item, itemSelector, repetition, suffix) {
        itemSelector.find('.copy').click(function(e) {
            var itemCopy = _layoutItem(item, repetition + 1, suffix);

            itemSelector.find('input, select').each(function() {
                inputCopy = itemCopy.find("[name='" + $(this).attr('name') + "']");
                inputCopy.val($(this).val());

                if(!$(this).parent().parent().find('.children-anchor-point').is(':hidden')) {
                    inputCopy.parent().parent().find('.children-anchor-point').show();
                }
            });
            itemCopy.find('.hidden').removeClass('hidden');
            itemSelector.after(itemCopy);
            _setupCopyRemoveEvents(item, itemCopy, repetition + 1, suffix);
        });

        itemSelector.find('.remove').click(function(e) {
            itemSelector.remove();
        });

        // initialise all datapickers
        itemSelector.find('.date').datetimepicker({
            format: 'DD/MM/YYYY'
        });
    }

    return {
        layoutFormItems: function(formContainerSelector, formStructure, data) {
            var formContainer = $(formContainerSelector);

            $.each(formStructure, function(index, item) {
                formContainer.append(_layoutItem(item, 0, '', data));
            });

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
        },
        initialiseSidebarMenu: function(sidebarMenuSelector) {
            $('.section').each(function(index, value) {
                var link = $('<a>');
                link.attr('href', '#section-' + index);
                link.text($(this).text());
                $('#sectionList ul').append($('<li>').append(link));
            });

            var sectionList = $(sidebarMenuSelector);
            $('body').scrollspy({ target: '#sectionList' });
            sectionList.affix({ offset: { top: sectionList.offset().top }});
        }
    }
});