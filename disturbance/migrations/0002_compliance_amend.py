from __future__ import unicode_literals
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='compliance',
            name='reminder_sent',
            field=models.BooleanField(default=False),
        ),
    ]
