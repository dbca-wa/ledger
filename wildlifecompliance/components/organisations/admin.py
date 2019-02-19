from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.organisations import models
# Register your models here.


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OrganisationRequest)
class OrganisationRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OrganisationAccessGroup)
class OrganisationAccessGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    exclude = ('site',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            kwargs["queryset"] = EmailUser.objects.filter(
                email__icontains='@dbca.wa.gov.au')
        return super(
            OrganisationAccessGroupAdmin,
            self).formfield_for_manytomany(
            db_field,
            request,
            **kwargs)

    def has_add_permission(self, request):
        return True if models.OrganisationAccessGroup.objects.count() == 0 else False


@admin.register(models.OrganisationContact)
class OrganisationContactAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserDelegation)
class UserDelegationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OrganisationAction)
class UOrganisationActionAdmin(admin.ModelAdmin):
    pass
