from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.forms import modelform_factory

from reversion.admin import VersionAdmin

from social.apps.django_app.default.models import UserSocialAuth

from ledger.accounts.models import EmailUser, Address, Profile


@admin.register(EmailUser)
class EmailUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',),
        }),
    )
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {'fields': ('first_name', 'last_name',)}),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # need to override add_form/form because the UserAdmin uses custom forms requiring passwords
    add_form = modelform_factory(EmailUser, fields=[])
    form = add_form

    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name', 'email')

    def _create_user_social_auth(self, user):
        user_social_auth = UserSocialAuth.create_social_auth(user, user.email, 'email')
        user_social_auth.extra_data = {'email': [user.email]}
        user_social_auth.save()

        return user_social_auth

    def save_model(self, request, obj, form, change):
        obj.save()

        if not UserSocialAuth.objects.filter(user_id=obj).exists():
            self._create_user_social_auth(obj)
        else:
            try:
                user_social_auth = UserSocialAuth.objects.get(user=obj)
                user_social_auth.uid = obj.email
                user_social_auth.extra_data = {'email': [obj.email]}
                user_social_auth.save()
            except UserSocialAuth.DoesNotExist:
                self._create_user_social_auth(obj)


@admin.register(Address)
class AddressAdmin(VersionAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(VersionAdmin):
    pass
