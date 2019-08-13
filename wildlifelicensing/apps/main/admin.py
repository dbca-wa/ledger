from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import WildlifeLicenceCategory, WildlifeLicenceType, Condition, \
    DefaultCondition, Region, Variant, VariantGroup
from wildlifelicensing.apps.main.forms import BetterJSONField

from wildlifelicensing.apps.payments import utils as payment_utils


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


class VariantGroupAdminForm(forms.ModelForm):
    class Meta:
        model = VariantGroup
        exclude = []

    def clean(self):
        """
        Checks if there are any licence types with this group or one it this group's parents set and
        makes sure there's products for every variant of those licence types.
        type.
        :return:
        """
        if self.instance is not None:
            related_variant_groups = []

            def __get_group_and_parent_groups(current_variant_group, groups):
                groups.append(current_variant_group)
                for group in VariantGroup.objects.filter(child=current_variant_group):
                    __get_group_and_parent_groups(group, groups)

            __get_group_and_parent_groups(self.instance, related_variant_groups)

            # keep previous variants in case the validation fails
            if hasattr(self.instance, 'variants'):
                previous_variants = list(self.instance.variants.all())

                self.instance.variants = self.cleaned_data['variants']

            missing_product_variants = []

            for licence_type in WildlifeLicenceType.objects.filter(variant_group__in=related_variant_groups):
                variant_codes = payment_utils.generate_product_title_variants(licence_type)

                for variant_code in variant_codes:
                    if payment_utils.get_product(variant_code) is None:
                        missing_product_variants.append(variant_code)

            if missing_product_variants:
                msg = mark_safe("The payments products with titles matching the below list of product codes were not "
                                "found. Note: You must create a payment product(s) for variants of each licence type linked "
                                "to this variant group, even if the licence has no fee. <ul><li>{}</li></ul>".
                                format('</li><li>'.join(missing_product_variants)))

                if hasattr(self.instance, 'variants'):
                    # revert back to previous variants list
                    self.instance.variants = previous_variants

                raise ValidationError(msg)


@admin.register(VariantGroup)
class VariantGroupAdmin(VersionAdmin):
    list_display = ('name',)
    filter_horizontal = ('variants',)
    form = VariantGroupAdminForm


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
