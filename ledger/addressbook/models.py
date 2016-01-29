from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Address(models.Model):
    """Generic address model, intended to provide billing an shipping
    addresses.
    Taken from django-oscar address AbstrastAddress class.
    """
    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    STATE_CHOICES = (
        ('ACT', 'ACT'),
        ('NSW', 'NSW'),
        ('NT', 'NT'),
        ('QLD', 'QLD'),
        ('SA', 'SA'),
        ('TAS', 'TAS'),
        ('VIC', 'VIC'),
        ('WA', 'WA')
    )

    title = models.CharField(
        max_length=64, choices=TITLE_CHOICES, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    # Addresses consist of 1+ lines, only the first of which is
    # required.
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    line3 = models.CharField(max_length=255, blank=True)
    locality = models.CharField(max_length=255, blank=True)
    state = models.CharField(
        max_length=255, choices=STATE_CHOICES, blank=True)
    postcode = models.IntegerField(blank=True)
    # A field only used for searching addresses.
    search_text = models.TextField(editable=False)

    def __str__(self):
        return self.summary

    class Meta:
        verbose_name_plural = 'addresses'

    def clean(self):
        # Strip all whitespace
        for field in ['first_name', 'last_name', 'line1', 'line2', 'line3',
                      'locality', 'state']:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].strip()

    def save(self, *args, **kwargs):
        self._update_search_text()
        super(Address, self).save(*args, **kwargs)

    def _update_search_text(self):
        search_fields = filter(
            bool, [self.first_name, self.last_name,
                   self.line1, self.line2, self.line3, self.locality,
                   self.state, self.postcode])
        self.search_text = ' '.join(search_fields)

    @property
    def summary(self):
        """Returns a single string summary of the address, separating fields
        using commas.
        """
        return u', '.join(self.active_address_fields())

    @property
    def salutation(self):
        """Name (including title)
        """
        return self.join_fields(
            ('title', 'first_name', 'last_name'),
            separator=u' ')

    @property
    def name(self):
        return self.join_fields(('first_name', 'last_name'), separator=u' ')

    # Helper methods
    def active_address_fields(self, include_salutation=True):
        """Return the non-empty components of the address, but merging the
        title, first_name and last_name into a single line.
        """
        fields = [self.line1, self.line2, self.line3,
                  self.locality, self.state, self.postcode]
        if include_salutation:
            fields = [self.salutation] + fields
        fields = [f.strip() for f in fields if f]
        return fields

    def join_fields(self, fields, separator=u", "):
        """Join a sequence of fields using the specified separator.
        """
        field_values = []
        for field in fields:
            # Title is special case
            if field == 'title':
                value = self.get_title_display()
            else:
                value = getattr(self, field)
            field_values.append(value)
        return separator.join(filter(bool, field_values))
