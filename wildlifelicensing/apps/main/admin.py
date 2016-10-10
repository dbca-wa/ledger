from django.contrib import admin
from django import forms

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import WildlifeLicenceCategory, WildlifeLicenceType, Condition, \
    DefaultCondition, Region, Variant, VariantGroup
from wildlifelicensing.apps.main.forms import BetterJSONField


class DefaultConditionInline(admin.TabularInline):
    model = DefaultCondition
    ordering = ('order',)


class PreviousLicenceTypeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{} (V{})'.format(obj.short_name or obj.name, obj.version)


@admin.register(Region)
class RegionAdmin(VersionAdmin):
    list_display = ['name']
    ordering = ['name']


@admin.register(WildlifeLicenceCategory)
class WildlifeLicenceCategoryAdmin(VersionAdmin):
    pass


class WildlifeLicenceTypeAdminForm(forms.ModelForm):
    application_schema = BetterJSONField()
    replaced_by = PreviousLicenceTypeChoiceField(queryset=WildlifeLicenceType.objects.all())

    def __init__(self, *args, **kwargs):
        super(WildlifeLicenceTypeAdminForm, self).__init__(*args, **kwargs)
        if self.instance.id:
            self.fields['replaced_by'].queryset = WildlifeLicenceType.objects.exclude(id=self.instance.id)
        self.fields['replaced_by'].required = False

    class Meta:
        model = WildlifeLicenceType
        exclude = []

    def clean_application_schema(self):
        schema = self.cleaned_data['application_schema']

        names = []

        def __check_name(schema):
            if type(schema) is list:
                for item in schema:
                    __check_name(item)
            elif type(schema) is dict:
                if 'type' in schema:
                    if 'name' in schema:
                        if schema['name'] in names:
                            raise forms.ValidationError('Duplicate Name %s' % schema.get('name'))
                        else:
                            names.append(schema['name'])
                    else:
                        raise forms.ValidationError('Missing Name %s with label %s' % (schema.get('type'), schema.get('label')))
                if 'children' in schema:
                    for item in schema['children']:
                        __check_name(item)
                if 'conditions' in schema:
                    for condition, condition_values in schema['conditions'].items():
                        if type(condition_values) is list:
                            for item in condition_values:
                                __check_name(item)
                        else:
                            raise forms.ValidationError('Condition values must be a list for condition %s of %s' %
                                                        (condition, schema.get('name')))

        __check_name(schema)

        return schema


@admin.register(WildlifeLicenceType)
class WildlifeLicenceTypeAdmin(VersionAdmin):
    list_display = ('name', 'display_name', 'version', 'code')
    filter_horizontal = ('default_conditions',)
    inlines = (DefaultConditionInline,)
    form = WildlifeLicenceTypeAdminForm


@admin.register(Variant)
class VariantAdmin(VersionAdmin):
    list_display = ('name',)


@admin.register(VariantGroup)
class VariantGroupAdmin(VersionAdmin):
    list_display = ('name',)
    filter_horizontal = ('variants',)


@admin.register(Condition)
class ConditionAdmin(VersionAdmin):
    list_display = ['code', 'text']
    search_fields = ['code', 'text']
    ordering = ['code']
    actions = ['make_obsolete']

    def get_actions(self, request):
        actions = super(ConditionAdmin, self).get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions

    def make_obsolete(self, request, queryset):
            queryset.update(obsolete=True)

    def has_delete_permission(self, request, obj=None):
        return False

    make_obsolete.short_description = 'Mark selected conditions as obsolete'
