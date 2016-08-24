from django.contrib import admin
from django import forms

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.forms import BetterJSONField
from wildlifelicensing.apps.returns.models import ReturnType


class ReturnTypeAdminForm(forms.ModelForm):
    data_descriptor = BetterJSONField()

    class Meta:
        model = ReturnType
        exclude = []


@admin.register(ReturnType)
class ReturnTypeAdmin(VersionAdmin):
    list_display = ('licence_type',)
    form = ReturnTypeAdminForm
