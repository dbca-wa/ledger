from __future__ import unicode_literals
from django.contrib.postgres.fields import JSONField
from oscar.apps.customer.abstract_models import AbstractUser


class EmailUser(AbstractUser):
    """A subclass of the django-oscar AbstractUser model, which uses email
    instead of username as an index.
    Also includes a field named extra_data to store ad-hoc unstructured data
    related to a user.
    """
    extra_data = JSONField(default=dict)

    def _migrate_alerts_to_user(self):
        """Override this private custom method on the parent class
        (attempts to update unused models).
        """
        pass
