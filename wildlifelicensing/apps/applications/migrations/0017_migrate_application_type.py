# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.db import migrations

logger = logging.getLogger(__name__)


def update_type_and_status(apps, schema_editor):
    """
    - Update application_type for amendment and renewal application.
    By default the new application_type is set to 'new licence' (see previous migration) but this type should be
    updated to amendment or renewal for some applications.
    - We also need to update the now obsolete processing status ['renewal', 'licence_amendment'] to 'new'
    :param apps:
    :param schema_editor:
    :return:
    """
    obsolete_processing_status = ['renewal', 'licence_amendment']
    Application = apps.get_model("wl_applications", "Application")
    # search for application with a previous_application
    apps = Application.objects.filter(previous_application__isnull=False)
    # these applications are either amendment or renewal depending of the 'is_licence_amendment' flag.
    for app in apps:
        app.application_type = 'amendment' if app.is_licence_amendment else 'renewal'
        # we update also the processing status to 'new' if it is one of the now obsolete status
        if app.processing_status in obsolete_processing_status:
            app.processing_status = 'new'
        app.save()

    # double check status for applications without previous app
    should_not_be = Application.objects.exclude(previous_application__isnull=False).filter(
        processing_status__in=obsolete_processing_status)
    if should_not_be:
        logger.error("Some applications without parents have a status in {}: {}".
                     format(obsolete_processing_status, should_not_be.values('pk')))
        should_not_be.update(processing_status='new')


def roll_back(apps, schema_editor):
    # nothing we can do
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('wl_applications', '0016_application_application_type'),
    ]

    operations = [
        migrations.RunPython(update_type_and_status, roll_back)
    ]
