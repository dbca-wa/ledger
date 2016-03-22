from django.contrib import admin

from reversion.admin import VersionAdmin

from models import Application


@admin.register(Application)
class ApplicationAdmin(VersionAdmin):
    pass
