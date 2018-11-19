# -*- coding: utf-8 -*-
# Manually Created
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mooring', '0020_create_views'),
    ]

    operations = [
        migrations.RunSQL(
            """CREATE OR REPLACE VIEW mooring_mooringsiteclass_pricehistory_v AS
                    SELECT DISTINCT classes.campsite_class_id AS id,
                        classes.date_start,
                        classes.date_end,
                        r.id AS rate_id,
                        r.adult,
                        r.concession,
                        r.child,
                        classes.details,
                        classes.reason_id
                    FROM mooring_rate r
                    INNER JOIN (
                        SELECT distinct cc.id AS campsite_class_id,
                            cr.rate_id AS campsite_rate_id,
                            cr.date_start AS date_start,
                            cr.date_end AS date_end,
                            cr.details AS details,
                            cr.reason_id AS reason_id
                        FROM mooring_mooringsite cs,
                            mooring_mooringsiteclass cc,
                            mooring_mooringsiterate cr
                        WHERE cs.mooringsite_class_id = cc.id AND
                            cr.campsite_id = cs.id AND
                            cr.update_level = 1
                    ) classes ON r.id = classes.campsite_rate_id"""
        ),
        migrations.RunSQL(
            """CREATE OR REPLACE VIEW mooring_mooringarea_pricehistory_v AS
                    SELECT DISTINCT camps.campground_id AS id,
                        cr.date_start,
                        cr.date_end,
                        r.id AS rate_id,
                        r.adult,
                        r.concession,
                        r.child,
                        cr.details,
                        cr.reason_id
                    FROM mooring_mooringsiterate cr
                    INNER JOIN mooring_rate r ON r.id = cr.rate_id
                    INNER JOIN (
                        SELECT cg.id AS campground_id,
                            cs.name AS name,
                            cs.id AS campsite_id
                        FROM mooring_mooringsite cs,
                            mooring_mooringarea cg
                        WHERE cs.mooringarea_id = cg.id AND
                            cg.id = cs.mooringarea_id AND
                            cg.price_level = 0
                    ) camps ON cr.campsite_id = camps.campsite_id"""
        )
    ]
