from __future__ import unicode_literals
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone


class EmailUserManager(BaseUserManager):
    """A custom Manager for the EmailUser model.
    """
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves an EmailUser with the given email and password.
        """
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email, is_staff=is_staff, is_superuser=is_superuser)
        user.extra_data = extra_fields
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=100, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    file = models.FileField(upload_to='%Y/%m/%d')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    @property
    def path(self):
        return self.file.path

    @property
    def filename(self):
        return self.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


@python_2_unicode_compatible
class Address(models.Model):
    """Generic address model, intended to provide billing and shipping
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
    postcode = models.IntegerField(null=True, blank=True)
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
                   self.state, str(self.postcode)])
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
            ('title', 'first_name', 'last_name'), separator=u' ')

    @property
    def name(self):
        return self.join_fields(('first_name', 'last_name'), separator=u' ')

    # Helper methods
    def active_address_fields(self, include_salutation=True):
        """Return the non-empty components of the address, but merging the
        title, first_name and last_name into a single line.
        """
        fields = [self.line1, self.line2, self.line3,
                  self.locality, self.state, str(self.postcode)]
        if include_salutation:
            fields = [self.salutation] + fields
        fields = [f.strip() for f in fields if f]
        return fields

    def join_fields(self, fields, separator=u', '):
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


@python_2_unicode_compatible
class EmailUser(AbstractBaseUser, PermissionsMixin):
    """Custom authentication model for the ledger project.
    Password and email are required. Other fields are optional.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=128, blank=True)
    last_name = models.CharField(max_length=128, blank=True)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.',
    )
    date_joined = models.DateTimeField(default=timezone.now)

    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    title = models.CharField(max_length=100, choices=TITLE_CHOICES, null=True, blank=False, default=TITLE_CHOICES[0][0],
                             verbose_name='title', help_text="")
    dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False,
                           verbose_name="date of birth", help_text='')
    phone_number = models.CharField(max_length=50, null=True, blank=True,
                                    verbose_name="phone number", help_text='')
    mobile_number = models.CharField(max_length=50, null=True, blank=True,
                                     verbose_name="mobile number", help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True,
                                  verbose_name="fax number", help_text='')
    organisation = models.CharField(max_length=300, null=True, blank=True,
                                    verbose_name="organisation", help_text='organisation, institution or company')

    residential_address = models.ForeignKey(Address, null=True, blank=False, related_name='+')
    postal_address = models.ForeignKey(Address, null=True, blank=True, related_name='+')
    billing_address = models.ForeignKey(Address, null=True, blank=True, related_name='+')

    documents = models.ManyToManyField(Document)

    extra_data = JSONField(default=dict)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        if self.organisation:
            return '{} ({})'.format(self.email, self.organisation)
        return '{}'.format(self.email)

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        if self.first_name:
            return self.first_name
        return self.email

    @property
    def username(self):
        return self.email



