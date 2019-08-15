from django.contrib import messages
from django.contrib.gis import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from django.db.models import Q

from ledger.accounts import admin as ledger_admin
from ledger.accounts.models import EmailUser
from copy import deepcopy

from mooring import models

class MooringAdminSite(AdminSite):
    site_header = 'Moorings Administration'
    site_title = 'Moorings Bookings'

mooring_admin_site = MooringAdminSite(name='mooringadmin')
admin.site.unregister(EmailUser)
@admin.register(EmailUser)
class EmailUserAdmin(ledger_admin.EmailUserAdmin):
    """
    Override the EmailUserAdmin from ledger.accounts.admin to remove is_superuser checkbox field on Admin page
    """
    def get_fieldsets(self, request, obj=None):
        """ Remove the is_superuser checkbox from the Admin page, is user is Mooring Admin or RIA Admin and NOT superuser."""
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        if not obj:
            return fieldsets
        
        if request.user.is_superuser:
            return fieldsets

        group = Group.objects.filter(name='Mooring Admin')
        if group and (group[0] in request.user.groups.all()):
            fieldsets = deepcopy(fieldsets)
            for fieldset in fieldsets:
                if 'is_superuser' in fieldset[1]['fields']:
                    if type(fieldset[1]['fields']) == tuple:
                        fieldset[1]['fields'] = list(fieldset[1]['fields'])
                    fieldset[1]['fields'].remove('is_superuser')
                    break
        return fieldsets

@admin.register(models.MooringsiteClass)
class MooringsiteClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(models.MarinePark)
class MarinaAdmin(admin.GeoModelAdmin):
    list_display = ('name','district','mooring_group')
    ordering = ('name',)
    list_filter = ('district',)
    search_fields = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    exclude = ('ratis_id',)

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(MarinaAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(MarinaAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(MarinaAdmin, self).save_model(request, obj, form, change)

@admin.register(models.MooringArea)
class MooringAreaAdmin(admin.GeoModelAdmin):
    list_display = ('name','park','promo_area','mooring_type','max_advance_booking')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('mooring_type','site_type')
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

@admin.register(models.MooringAreaGroup)
class MooringAreaGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members','moorings')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(MooringAreaGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(MooringAreaGroupAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(id__in=group)

@admin.register(models.Mooringsite)
class MooringsiteAdmin(admin.GeoModelAdmin):
    list_display = ('name','mooringarea',)
    ordering = ('name',)
    list_filter = ('mooringarea',)
    search_fields = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    ordering = ('name',)
    search_fields = ('name',)

class BookingInvoiceInline(admin.TabularInline):
    model = models.BookingInvoice
    extra = 0

class MooringsiteBookingInline(admin.TabularInline):
    model = models.MooringsiteBooking
    extra = 0

@admin.register(models.MooringsiteRateLog)
class MooringsiteRateLogAdmin(admin.ModelAdmin):
    list_display = ('id','mooringarea','change_type','booking_period','date_start','date_end','reason','details','created')
    ordering = ('-id',)

@admin.register(models.ChangeGroup)
class ChangeGroupAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    ordering = ('-id',)

@admin.register(models.ChangePricePeriod)
class ChangePricePeriodAdmin(admin.ModelAdmin):
    list_display = ('id','percentage','days')
    ordering = ('-days',)

@admin.register(models.CancelGroup)
class CancelGroupAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    ordering = ('-id',)

@admin.register(models.CancelPricePeriod)
class CancelPricePeriodAdmin(admin.ModelAdmin):
    list_display = ('id','percentage','days')
    ordering = ('-days',)

@admin.register(models.Booking)
class BookingAdmin(admin.ModelAdmin):
    raw_id_fields = ('customer','created_by','overridden_by','canceled_by','old_booking','admission_payment',)
    list_display = ('id','arrival','departure','booking_type','mooringarea','legacy_id','legacy_name','status','cost_total')
    ordering = ('-id',)
    search_fileds = ('arrival','departure')
    list_filter = ('id','arrival','departure','mooringarea')
    readonly_fields=('created',)
    inlines = [BookingInvoiceInline,MooringsiteBookingInline]

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(models.MooringsiteBooking)
class MooringsiteBookingAdmin(admin.ModelAdmin):
    list_display = ('campsite','date','booking','booking_type')
    ordering = ('-date',)
    search_fields = ('date',)
    list_filter = ('campsite','booking_type')

@admin.register(models.MooringsiteRate)
class MooringsiteRateAdmin(admin.ModelAdmin):
    list_display = ('campsite','rate','allow_public_holidays','booking_period')
    list_filter = ('campsite','rate','allow_public_holidays','booking_period')
    search_fields = ('campsite__name',)

@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name','phone_number')
    search_fields = ('name','phone_number')

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(ContactAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(ContactAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(ContactAdmin, self).save_model(request, obj, form, change)

class ReasonAdmin(admin.ModelAdmin):
    list_display = ('code','text','editable')
    search_fields = ('code','text')
    readonly_fields = ('code',)

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj and not obj.editable:
            fields += ['text','editable']
        elif not obj:
            fields = []
        return fields

    def has_add_permission(self, request, obj=None):
        if obj and not obj.editable:
            return False
        return super(ReasonAdmin, self).has_delete_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not obj.editable:
            return False
        return super(ReasonAdmin, self).has_delete_permission(request, obj)

@admin.register(models.MaximumStayReason)
class MaximumStayReason(ReasonAdmin):
    pass

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(MaximumStayReason, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(MaximumStayReason, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(MaximumStayReason, self).save_model(request, obj, form, change)

@admin.register(models.PriceReason)
class PriceReason(ReasonAdmin):
    pass

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(PriceReason, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(PriceReason, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(PriceReason, self).save_model(request, obj, form, change)

@admin.register(models.ClosureReason)
class ClosureReason(ReasonAdmin):
    pass

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(ClosureReason, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(ClosureReason, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(ClosureReason, self).save_model(request, obj, form, change)

@admin.register(models.OpenReason)
class OpenReason(ReasonAdmin):
    pass

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(OpenReason, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(OpenReason, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(OpenReason, self).save_model(request, obj, form, change)

@admin.register(models.DiscountReason)
class DiscountReason(ReasonAdmin):
    pass

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(DiscountReason, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(DiscountReason, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(DiscountReason, self).save_model(request, obj, form, change)

@admin.register(models.OutstandingBookingRecipient)
class OutstandingBookingRecipient(admin.ModelAdmin):
    pass

@admin.register(models.AdmissionsOracleCode)
class AdmissionsOracleCode(admin.ModelAdmin):
    list_display = ('oracle_code', 'mooring_group')

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(AdmissionsOracleCode, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(AdmissionsOracleCode, self).formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(models.AdmissionsRate)
class AdmissionsRate(admin.ModelAdmin):
    list_display = ('period_start', 'period_end')

@admin.register(models.AdmissionsReason)
class AdmissionsReason(admin.ModelAdmin):
    list_display = ('id', 'text')

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(AdmissionsReason, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(AdmissionsReason, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(AdmissionsReason, self).save_model(request, obj, form, change)

class AdmissionLineInline(admin.TabularInline):
    model = models.AdmissionsLine
    extra = 0

@admin.register(models.AdmissionsBooking)
class AdmissionBooking(admin.ModelAdmin):
    raw_id_fields = ('customer',)
    list_display = ('confirmation_number', 'customer', 'totalCost')
    readonly_fields=('created_by','canceled_by',)
    inlines = [AdmissionLineInline]


@admin.register(models.BookingPeriod)
class BookingPeriod(admin.ModelAdmin):
    list_display = ('name', 'created')
    search_fields = ('name',)

@admin.register(models.BookingPeriodOption)
class BookingPeriodOption(admin.ModelAdmin):
    list_display = ('option_description', 'period_name', 'small_price','medium_price','large_price','created')
    search_fields = ('option_description', 'period_name',)

@admin.register(models.Region)
class Region(admin.GeoModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
#    list_filter = ('mooring_type','site_type')
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    exclude = ('ratis_id',)

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(Region, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(Region, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(Region, self).save_model(request, obj, form, change)

@admin.register(models.District)
class District(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    exclude = ('ratis_id',)
    search_fields = ('name',)

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(District, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(District, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(District, self).save_model(request, obj, form, change)



admin.site.register(models.Rate)
#admin.site.register(models.Region)
#admin.site.register(models.District)
#admin.site.register(models.PromoArea)
@admin.register(models.PromoArea)
class PromoArea(admin.GeoModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    search_fields = ('name',)
    
    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(PromoArea, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return qs.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(PromoArea, self).formfield_for_foreignkey(db_field, request, **kwargs)
        
    def save_model(self, request, obj, form, change):
        if obj.mooring_group == None:
            groups = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
            if groups.count() == 1:
                obj.mooring_group = groups[0]
        super(PromoArea, self).save_model(request, obj, form, change)


@admin.register(models.RegisteredVessels)
class RegisteredVessels(admin.ModelAdmin):
    list_display = ('rego_no', 'sticker_l', 'sticker_au', 'sticker_an','vessel_size','vessel_draft','vessel_beam','vessel_weight')
    ordering = ('rego_no',)
    search_fields = ('rego_no',)

@admin.register(models.MooringAreaBookingRange)
class MooringAreaBookingRange(admin.ModelAdmin):
    list_display = ('id', 'range_start', 'range_end', 'campground_id')
    ordering = ('id',)

@admin.register(models.GlobalSettings)
class GlobalSettings(admin.ModelAdmin):
    list_display = ('key', 'value', 'mooring_group')

    def get_queryset(self, request):
        """ Filter based on the mooring group of the user. """
        qs = super(GlobalSettings, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        group = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        blacklist = qs.filter(key__in=[15, 16])
        whitelist = qs.exclude(id__in=blacklist)
        return whitelist.filter(mooring_group__in=group)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'mooring_group':
            kwargs['queryset'] = models.MooringAreaGroup.objects.filter(members__in=[request.user,])
        return super(GlobalSettings, self).formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(models.AdmissionsLocation)
class AdmissionsLocation(admin.ModelAdmin):
    list_display = ('text', 'mooring_group')
   
@admin.register(models.RefundFailed)
class RefundFailed(admin.ModelAdmin):
    list_display = ('booking', 'invoice_reference','refund_amount','status','created','completed_date','completed_by')
    search_fields = ('booking','invoice_reference','refund_amount')
    list_filter = ('status',)
    ordering = ('id',)

