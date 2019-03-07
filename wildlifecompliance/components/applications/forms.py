from django import forms
from wildlifecompliance.components.applications.models import (
    ActivityPermissionGroup
)
from django.contrib.auth.models import Permission

from django.forms.models import ModelMultipleChoiceField
from django.contrib.admin.widgets import FilteredSelectMultiple


class GroupPermissionsField(ModelMultipleChoiceField):
    widget = FilteredSelectMultiple(verbose_name='Group Permissions / Roles', is_stacked=True)


class ActivityPermissionGroupAdminForm(forms.ModelForm):
    permissions = GroupPermissionsField(
        queryset=Permission.objects.filter(content_type__model='activitypermissiongroup')
    )

    class Meta:
        model = ActivityPermissionGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ActivityPermissionGroupAdminForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(ActivityPermissionGroupAdminForm, self).clean()


def clean_email(self):
    return self.initial['email']