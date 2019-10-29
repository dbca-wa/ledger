from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.forms import modelform_factory
from django.conf import settings
from django.contrib.auth.models import Group

from reversion.admin import VersionAdmin

from ledger.accounts.models import EmailUser, Document, Address, Profile
from ledger.accounts.forms import ProfileAdminForm


@admin.register(EmailUser)
class EmailUserAdmin(UserAdmin):
    change_list_template = "ledger/accounts/change_emailuser_list.html"

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',),
        }),
    )
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'dob', 'identification','position_title', 'character_flagged', 'character_comments')}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets_for_dummy_user = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
    )
    fieldsets_for_dummy_user = (
        (None, {'fields': ('dummy_email', 'email',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'dob', 'identification', 'character_flagged', 'character_comments')}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # need to override add_form/form because the UserAdmin uses custom forms requiring passwords
    add_form = modelform_factory(EmailUser, fields=[])
    form = add_form

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_dummy')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name', 'email')
    readonly_fields = ('dummy_email',)

    def is_dummy(self, o):
        return o.is_dummy_user
    is_dummy.boolean = True

    def get_fieldsets(self, request, obj=None):
        if not obj:
            if request.GET.get('dummy', False):
                return self.add_fieldsets_for_dummy_user
            else:
                return self.add_fieldsets
        elif obj.is_dummy_user:
            return self.fieldsets_for_dummy_user
        else:
            return self.fieldsets

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # new user
            is_dummy = request.GET.get("dummy", False)
            if is_dummy:
                obj.email = obj.get_dummy_email()

        obj.save()

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if settings.SYSTEM_GROUPS and db_field.name == "groups" and not request.user.is_superuser:
            kwargs["queryset"] = Group.objects.filter(name__in=settings.SYSTEM_GROUPS)
        return super(EmailUserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    model = Document


@admin.register(Address)
class AddressAdmin(VersionAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(VersionAdmin):
    form = ProfileAdminForm

    list_display = ('user', 'name', 'email', 'institution', 'postal_address')
    ordering = ('user',)
    search_fields = ('user__email', 'name', 'email', 'institution')
