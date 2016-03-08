define(['jQuery', 'js/utils', 'bootstrap'], function($, utils) {
    function setupConditionalFields(formSections) {
        $.each(formSections, function(index, section) {
            if ('conditional_fields' in section) {
                $.each(section.conditional_fields, function(index, conditionalField) {
                    $("[name='" + conditionalField.conditional_field + "']").change(function(e) {
                        if ($(this).val() === conditionalField.condition) {
                            $.each(conditionalField.target_fields, function(index, targetField) {
                                setFormGroupDisabledState($("[name='" + targetField + "']"), false);
                            });
                        } else {
                            $.each(conditionalField.target_fields, function(index, targetField) {
                                setFormGroupDisabledState($("[name='" + targetField + "']"), true);
                            });
                        }
                    });
                });
            }
        });
    }

    function setFormGroupDisabledState(inputField, isDisabled) {
        inputField.prop('disabled', isDisabled);

        if(isDisabled) {
            inputField.closest('.form-group').addClass('disabled');
        } else {
            inputField.closest('.form-group').removeClass('disabled');
        }
    }

    function setupConditionalFieldsForClonedGroup(group, conditionalFields) {
        $.each(conditionalFields, function(index, conditionalField) {
            // set (or unset) the initial disabled state of the conditional fields
            var conditionalFieldSelector = group.find("[name='" + conditionalField.conditional_field + "']");
            if (conditionalFieldSelector) {
                if (conditionalFieldSelector.val() === conditionalField.condition) {
                    $.each(conditionalField.target_fields, function(index, targetField) {
                        setFormGroupDisabledState(group.find("[name='" + targetField + "']"), false);
                    });
                } else {
                    $.each(conditionalField.target_fields, function(index, targetField) {
                        setFormGroupDisabledState(group.find("[name='" + targetField + "']"), true);
                    });
                }

                // setup change event for the conditional fields
                conditionalFieldSelector.change(function(e) {
                    if ($(this).val() === conditionalField.condition) {
                        $.each(conditionalField.target_fields, function(index, targetField) {
                            setFormGroupDisabledState(group.find("[name='" + targetField + "']"), false);
                        });
                    } else {
                        $.each(conditionalField.target_fields, function(index, targetField) {
                            setFormGroupDisabledState(group.find("[name='" + targetField + "']"), true);
                        });
                    }
                });
            }
        });
    }

    function setupAdditionalGroups(formSections) {
        $.each(formSections, function(index, section) {
            if ('groups' in section ) {
                $.each(section.groups, function(name, group) {
                    if (group.can_create_additional) {
                        setupAdditionalGroup(name, section.conditional_fields);
                    }
                });
            }
        });
    }

    function setupAdditionalGroup(groupName, conditionalFields) {
        $('#add-' + utils.slugify(groupName)).click(function(e) {
            // need to clone first group(with no remove link), but will later want to insert new group after last group 
            var allGroups = $('[id^=' + this.target + ']');
            var firstGroup = allGroups.filter(':first');
            var lastGroup = allGroups.filter(':last');

            var newGroup = firstGroup.clone();

            // set id of new group to have a suffix one higher than the last group
            var groupIDComponents = lastGroup.attr('id').split('-');
            var previousIDSuffix = parseInt(groupIDComponents[groupIDComponents.length - 1]);
            groupIDComponents[groupIDComponents.length - 1] = ++previousIDSuffix;
            newGroup.attr('id', groupIDComponents.join('-'));

            // clear all values
            newGroup.find('input').val('').end();

            setupConditionalFieldsForClonedGroup(newGroup, conditionalFields);

            removeLink = $('<a>Remove ' + groupName + '</a>').click(function() {
                newGroup.remove();
            });
            newGroup.children().children().last().after($('<div></div>').addClass('remove-group').append(removeLink));

            lastGroup.after(newGroup);
        });
    }

    return function(scrollSpyElement, scrollSpyTarget, affixElement, formSections) {
        $(scrollSpyElement).scrollspy({ target: scrollSpyTarget });
        $(affixElement).affix({ offset: { top: 120 }});

        setupConditionalFields(formSections);
        setupAdditionalGroups(formSections);
    }
});