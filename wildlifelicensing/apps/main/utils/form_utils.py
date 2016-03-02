from abc import ABCMeta, abstractmethod
from mock import self
from bottle import FormsDict
from django import forms


class SectionItem:
    __metaclass__ = ABCMeta

    @abstractmethod
    def type(self):
        pass


class Field(SectionItem):
    def __init__(self, form, field_name, disabled=False):
        self.form = form
        self.field_name = field_name
        self.disabled = disabled

    def type(self):
        return 'field'

    def as_bound_field(self):
        return self.form[self.field_name]


class Group(SectionItem):
    def __init__(self, form, section, name, fields, can_create_additional):
        self.form = form
        self.section = section
        self.name = name
        self.fields = fields
        self.can_create_additional = can_create_additional

    def type(self):
        return 'group'

    def get_name(self):
        return self.name

    def get_fields(self):
        for field in self.fields:
            yield Field(self.form, field, self.section.is_initially_disabled(field))

    def can_create_additional(self):
        return self.can_create_additional

    def __iter__(self):
        for field in self.get('fields', ()):
            yield self.form[field]

    def __len__(self):
        return len(self.get('fields', ()))


class Section(object):
    def __init__(self, form, name, items, groups, conditional_fields):
        self.form = form
        self.name = name
        self.items = items
        self.groups = groups
        self.conditional_fields = conditional_fields

    def get_items(self):
        for item in self.items:
            if self.groups is not None and item in self.groups:
                yield Group(self.form, self, item, self.groups[item].get('fields', ()), self.groups[item].get('can_create_additional', False))
            else:
                yield Field(self.form, item, self.is_initially_disabled(item))

    def is_initially_disabled(self, item):
        if self.conditional_fields is None:
            return False

        for conditional_field in self.conditional_fields:
            # if conditional_field is radiobutton, target fields should be initially disabled as no option is set by default
            if isinstance(self.form.fields[conditional_field['conditional_field']].widget, forms.RadioSelect):
                return item in conditional_field['target_fields']
            # if conditional field is choice field, it will be set to first choice, so need to make sure first choice isn't already the condition
            elif conditional_field['condition'] != self.form.fields[conditional_field['conditional_field']].choices[0][0]:
                return item in conditional_field['target_fields']
            else:
                return False
        else:
            return False


class SectionedForm(object):
    def get_sections(self):
        for section in self.sections:
            yield Section(self, section.get('name'), section.get('items'), section.get('groups', None), section.get('conditional_fields', None))
