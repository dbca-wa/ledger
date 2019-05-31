from django import forms
from wildlifecompliance.components.users.models import (
    CompliancePermissionGroup
)
from django.contrib.auth.models import Permission

from django.forms.models import ModelMultipleChoiceField
from django.contrib.admin.widgets import FilteredSelectMultiple


class GroupPermissionsField(ModelMultipleChoiceField):
    widget = FilteredSelectMultiple(verbose_name='Group Permissions / Roles', is_stacked=True)


class CompliancePermissionGroupAdminForm(forms.ModelForm):
    permissions = GroupPermissionsField(
        queryset=Permission.objects.filter(content_type__model='compliancepermissiongroup')
    )

    class Meta:
        model = CompliancePermissionGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CompliancePermissionGroupAdminForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(CompliancePermissionGroupAdminForm, self).clean()


def clean_email(self):
    return self.initial['email']