from __future__ import unicode_literals

import os
import zlib

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models, IntegrityError, transaction
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.dispatch import receiver
from django.db.models import Q
from django.db.models.signals import post_delete, pre_save, post_save
from django.core.exceptions import ValidationError

from reversion import revisions
from reversion.models import Version
from django_countries.fields import CountryField

from social_django.models import UserSocialAuth

from datetime import datetime, date

from ledger.accounts.signals import name_changed, post_clean
from ledger.accounts.utils import get_department_user_compact, in_dbca_domain, get_app_label
from ledger.address.models import UserAddress, Country


class EmailUserManager(BaseUserManager):
    """A custom Manager for the EmailUser model.
    """
    use_in_migrations = True

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """Creates and saves an EmailUser with the given email and password.
        """
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email).lower()
        if (EmailUser.objects.filter(email__iexact=email) or
                Profile.objects.filter(email__iexact=email) or
                EmailIdentity.objects.filter(email__iexact=email)):
            raise ValueError('This email is already in use')
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
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


class DocumentListener(object):
    """
    Event listener for Document.

    """
    @staticmethod
    @receiver(post_delete, sender=Document)
    def _post_delete(sender, instance, **kwargs):
        # Pass false so FileField doesn't save the model.
        try:
            instance.file.delete(False)
        except NotImplementedError:
            #  if deleting file is failed, ignore.
            pass

    @staticmethod
    @receiver(pre_save, sender=Document)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Document.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Document)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if original_instance and original_instance.file and instance.file != original_instance.file:
            # file changed, delete the original file
            try:
                original_instance.file.delete(False)
            except NotImplementedError:
                # if deleting file is failed, ignore.
                pass
            delattr(instance, "_original_instance")


@python_2_unicode_compatible
class BaseAddress(models.Model):
    """Generic address model, intended to provide billing and shipping
    addresses.
    Taken from django-oscar address AbstrastAddress class.
    """
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

    # Addresses consist of 1+ lines, only the first of which is
    # required.
    line1 = models.CharField('Line 1', max_length=255)
    line2 = models.CharField('Line 2', max_length=255, blank=True)
    line3 = models.CharField('Line 3', max_length=255, blank=True)
    locality = models.CharField('Suburb / Town', max_length=255)
    state = models.CharField(max_length=255, default='WA', blank=True)
    country = CountryField(default='AU')
    postcode = models.CharField(max_length=10)
    # A field only used for searching addresses.
    search_text = models.TextField(editable=False)
    hash = models.CharField(max_length=255, db_index=True, editable=False)

    def __str__(self):
        return self.summary

    class Meta:
        abstract = True

    def clean(self):
        # Strip all whitespace
        for field in ['line1', 'line2', 'line3',
                      'locality', 'state']:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].strip()

    def save(self, *args, **kwargs):
        self._update_search_text()
        self.hash = self.generate_hash()
        super(BaseAddress, self).save(*args, **kwargs)

    def _update_search_text(self):
        search_fields = filter(
            bool, [self.line1, self.line2, self.line3, self.locality,
                   self.state, str(self.country.name), self.postcode])
        self.search_text = ' '.join(search_fields)

    @property
    def summary(self):
        """Returns a single string summary of the address, separating fields
        using commas.
        """
        return u', '.join(self.active_address_fields())

    # Helper methods
    def active_address_fields(self):
        """Return the non-empty components of the address.
        """
        fields = [self.line1, self.line2, self.line3,
                  self.locality, self.state, self.country, self.postcode]
        fields = [str(f).strip() for f in fields if f]
        return fields

    def join_fields(self, fields, separator=u', '):
        """Join a sequence of fields using the specified separator.
        """
        field_values = []
        for field in fields:
            value = getattr(self, field)
            field_values.append(value)
        return separator.join(filter(bool, field_values))

    def generate_hash(self):
        """
            Returns a hash of the address summary
        """
        return zlib.crc32(self.summary.strip().upper().encode('UTF8'))


class Address(BaseAddress):
    user = models.ForeignKey('EmailUser', related_name='profile_addresses')
    oscar_address = models.ForeignKey(UserAddress, related_name='profile_addresses')

    class Meta:
        verbose_name_plural = 'addresses'
        unique_together = ('user', 'hash')


@python_2_unicode_compatible
class EmailIdentity(models.Model):
    """Table used for matching access email address with EmailUser.
    """
    user = models.ForeignKey('EmailUser', null=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


@python_2_unicode_compatible
class EmailUser(AbstractBaseUser, PermissionsMixin):
    """Custom authentication model for the ledger project.
    Password and email are required. Other fields are optional.
    """
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
    is_staff = models.BooleanField(
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active.'
                  'Unselect this instead of deleting ledger.accounts.',
    )
    date_joined = models.DateTimeField(default=timezone.now)

    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    title = models.CharField(max_length=100, choices=TITLE_CHOICES, null=True, blank=True,
                             verbose_name='title', help_text='')
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

    identification = models.ForeignKey(
        Document,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='identification_document'
    )

    senior_card = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='senior_card')

    character_flagged = models.BooleanField(default=False)

    character_comments = models.TextField(blank=True)

    documents = models.ManyToManyField(Document)

    extra_data = JSONField(default=dict)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        if self.is_dummy_user:
            if self.organisation:
                return '{} {} ({})'.format(self.first_name, self.last_name, self.organisation)
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            if self.organisation:
                return '{} ({})'.format(self.email, self.organisation)
            return '{}'.format(self.email)

    def clean(self):
        super(EmailUser, self).clean()
        self.email = self.email.lower() if self.email else self.email
        post_clean.send(sender=self.__class__, instance=self)

    def save(self, *args, **kwargs):
        if not self.email:
            self.email = self.get_dummy_email()
        elif in_dbca_domain(self):
            # checks and updates department user details from address book after every login
            user_details = get_department_user_compact(self.email)
            if user_details:
                self.phone_number = user_details.get('telephone')
                self.mobile_number = user_details.get('mobile_phone')
                self.title = user_details.get('title')
                self.fax_number = user_details.get('org_unit__location__fax')

        super(EmailUser, self).save(*args, **kwargs)

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_full_name_dob(self):
        full_name_dob = '{} {} ({})'.format(self.first_name, self.last_name, self.dob.strftime('%d/%m/%Y'))
        return full_name_dob.strip()

    def get_short_name(self):
        if self.first_name:
            return self.first_name.split(' ')[0]
        return self.email

    def upload_identification(self, request):
        with transaction.atomic():
            document = Document(file=request.data.dict()['identification'])
            document.save()
            self.identification = document
            self.save()

    dummy_email_suffix = ".s058@ledger.dpaw.wa.gov.au"
    dummy_email_suffix_len = len(dummy_email_suffix)

    def has_wildlifelicenceactivity_perm(self, permission_codename, licence_activity_id):
        app_label = get_app_label()
        group_queryset = self.groups.filter(
            permissions__codename__in=permission_codename if isinstance(
                permission_codename, (list, models.query.QuerySet)
            ) else [permission_codename],
            activitypermissiongroup__licence_activities__id__in=licence_activity_id if isinstance(
                licence_activity_id, (list, models.query.QuerySet)
            ) else [licence_activity_id]
        )
        if app_label:
            group_queryset = group_queryset.filter(permissions__content_type__app_label=app_label)
        return group_queryset.count()

    def get_wildlifelicence_permission_group(self, permission_codename, activity_id=None, first=True):
        app_label = get_app_label()
        qs = self.groups.filter(
            permissions__codename=permission_codename
        )
        if activity_id is not None:
            qs = qs.filter(
                activitypermissiongroup__licence_activities__id__in=activity_id if isinstance(
                    activity_id, (list, models.query.QuerySet)
                ) else [activity_id]
            )
        if app_label:
            qs = qs.filter(permissions__content_type__app_label=app_label)
        return qs.first() if first else qs

    @property
    def is_dummy_user(self):
        return not self.email or self.email[-1 * self.dummy_email_suffix_len:] == self.dummy_email_suffix

    @property
    def dummy_email(self):
        if self.is_dummy_user:
            return self.email
        else:
            return None

    def get_dummy_email(self):
        # use timestamp plus first name, last name to generate a unique id.
        uid = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return "{}.{}.{}{}".format(self.first_name, self.last_name, uid, self.dummy_email_suffix)

    @property
    def username(self):
        return self.email

    @property
    def is_senior(self):
        """
        Test if the the user is a senior according to the rules of WA senior
        dob is before 1 July 1955; or
        dob is between 1 July 1955 and 30 June 1956 and age is 61 or older; or
        dob is between 1 July 1956 and 30 June 1957 and age is 62 or older; or
        dob is between 1 July 1957 and 30 June 1958 and age is 63 or older; or
        dob is between 1 July 1958 and 30 June 1959 and age is 64 or older; or
        dob is after 30 June 1959 and age is 65 or older

        :return:
        """
        return \
            self.dob < date(1955, 7, 1) or \
            ((date(1955, 7, 1) <= self.dob <= date(1956, 6, 30)) and self.age() >= 61) or \
            ((date(1956, 7, 1) <= self.dob <= date(1957, 6, 30)) and self.age() >= 62) or \
            ((date(1957, 7, 1) <= self.dob <= date(1958, 6, 30)) and self.age() >= 63) or \
            ((date(1958, 7, 1) <= self.dob <= date(1959, 6, 30)) and self.age() >= 64) or \
            (self.dob > date(1959, 6, 1) and self.age() >= 65)

    def age(self):
        if self.dob:
            today = date.today()
            # calculate age with the help of trick int(True) = 1 and int(False) = 0
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        else:
            return -1

    def log_user_action(self, action, request=None):
        if request:
            return EmailUserAction.log_action(self, action, request.user)
        else:
            pass


def query_emailuser_by_args(**kwargs):
    ORDER_COLUMN_CHOICES = [
        'title',
        'first_name',
        'last_name',
        'dob',
        'email',
        'phone_number',
        'mobile_number',
        'fax_number',
        'character_flagged',
        'character_comments'
    ]

    draw = int(kwargs.get('draw', None)[0])
    length = int(kwargs.get('length', None)[0])
    start = int(kwargs.get('start', None)[0])
    search_value = kwargs.get('search[value]', None)[0]
    order_column = kwargs.get('order[0][column]', None)[0]
    order = kwargs.get('order[0][dir]', None)[0]
    order_column = ORDER_COLUMN_CHOICES[int(order_column)]
    # django orm '-' -> desc
    if order == 'desc':
        order_column = '-' + order_column

    queryset = EmailUser.objects.all()
    total = queryset.count()

    if search_value:
        queryset = queryset.filter(Q(first_name__icontains=search_value) |
                                   Q(last_name__icontains=search_value) |
                                   Q(email__icontains=search_value) |
                                   Q(phone_number__icontains=search_value) |
                                   Q(mobile_number__icontains=search_value) |
                                   Q(fax_number__icontains=search_value))

    count = queryset.count()
    queryset = queryset.order_by(order_column)[start:start + length]

    return {
        'items': queryset,
        'count': count,
        'total': total,
        'draw': draw
    }


@python_2_unicode_compatible
class UserAction(models.Model):
    who = models.ForeignKey(EmailUser, null=False, blank=False)
    when = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    what = models.TextField(blank=False)

    def __str__(self):
        return "{what} ({who} at {when})".format(
            what=self.what,
            who=self.who,
            when=self.when
        )

    class Meta:
        abstract = True
        app_label = 'accounts'


class EmailUserAction(UserAction):
    ACTION_PERSONAL_DETAILS_UPDATE = "User {} Personal Details Updated"
    ACTION_CONTACT_DETAILS_UPDATE = "User {} Contact Details Updated"
    ACTION_POSTAL_ADDRESS_UPDATE = "User {} Postal Address Updated"
    ACTION_ID_UPDATE = "User {} Identification Updated"

    emailuser = models.ForeignKey(EmailUser, related_name='action_logs')

    class Meta:
        app_label = 'accounts'
        ordering = ['-when']

    @classmethod
    def log_action(cls, emailuser, action, user):
        return cls.objects.create(
            emailuser=emailuser,
            who=user,
            what=str(action)
        )


class EmailUserListener(object):
    """
    Event listener for EmailUser

    """
    @staticmethod
    @receiver(post_delete, sender=EmailUser)
    def _post_delete(sender, instance, **kwargs):
        # delete the profile's email from email identity and social auth
        if not instance.is_dummy_user:
            EmailIdentity.objects.filter(email=instance.email, user=instance).delete()
            UserSocialAuth.objects.filter(provider="email", uid=instance.email, user=instance).delete()

    @staticmethod
    @receiver(pre_save, sender=EmailUser)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = EmailUser.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=EmailUser)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        # add user's email to email identity and social auth if not exist
        if not instance.is_dummy_user:
            EmailIdentity.objects.get_or_create(email=instance.email, user=instance)
            if not UserSocialAuth.objects.filter(user=instance, provider="email", uid=instance.email).exists():
                user_social_auth = UserSocialAuth.create_social_auth(instance, instance.email, 'email')
                user_social_auth.extra_data = {'email': [instance.email]}
                user_social_auth.save()

        if original_instance and original_instance.email != instance.email:
            if not original_instance.is_dummy_user:
                # delete the user's email from email identity and social auth
                EmailIdentity.objects.filter(email=original_instance.email, user=original_instance).delete()
                UserSocialAuth.objects.filter(provider="email", uid=original_instance.email, user=original_instance).delete()
            # update profile's email if profile's email is original email
            Profile.objects.filter(email=original_instance.email, user=instance).update(email=instance.email)

        if original_instance and any([original_instance.first_name != instance.first_name,
                                      original_instance.last_name != instance.last_name]):
            # user changed first name or last name, send a named_changed signal.
            name_changed.send(sender=instance.__class__, user=instance)


class RevisionedMixin(models.Model):
    """
    A model tracked by reversion through the save method.
    """
    def save(self, **kwargs):
        if kwargs.pop('no_revision', False):
            super(RevisionedMixin, self).save(**kwargs)
        else:
            with revisions.create_revision():
                revisions.set_user(kwargs.pop('version_user', None))
                revisions.set_comment(kwargs.pop('version_comment', ''))
                super(RevisionedMixin, self).save(**kwargs)

    @property
    def created_date(self):
        return Version.objects.get_for_object(self).last().revision.date_created

    @property
    def modified_date(self):
        return Version.objects.get_for_object(self).first().revision.date_created

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Profile(RevisionedMixin):
    user = models.ForeignKey(EmailUser, verbose_name='User', related_name='profiles')
    name = models.CharField('Display Name', max_length=100, help_text='e.g Personal, Work, University, etc')
    email = models.EmailField('Email')
    postal_address = models.ForeignKey(Address, verbose_name='Postal Address', on_delete=models.PROTECT, related_name='profiles')
    institution = models.CharField(
        'Institution',
        max_length=200,
        blank=True,
        default='',
        help_text='e.g. Company Name, Tertiary Institution, Government Department, etc'
    )

    @property
    def is_auth_identity(self):
        """
        Return True if the email is an email identity; otherwise return False.
        """
        if not self.email:
            return False

        if not hasattr(self, "_auth_identity"):
            self._auth_identity = EmailIdentity.objects.filter(user=self.user, email=self.email).exists()

        return self._auth_identity

    def clean(self):
        super(Profile, self).clean()
        self.email = self.email.lower() if self.email else self.email
        post_clean.send(sender=self.__class__, instance=self)

    def __str__(self):
        if len(self.name) > 0:
            return '{} ({})'.format(self.name, self.email)
        else:
            return '{}'.format(self.email)


@python_2_unicode_compatible
class Organisation(models.Model):
    """This model represents the details of a company or other organisation.
    Management of these objects will be delegated to 0+ EmailUsers.
    """
    name = models.CharField(max_length=128, unique=True)
    abn = models.CharField(max_length=50, null=True, blank=True, verbose_name='ABN')
    # TODO: business logic related to identification file upload/changes.
    identification = models.FileField(upload_to='%Y/%m/%d', null=True, blank=True)
    postal_address = models.ForeignKey(
        'OrganisationAddress',
        related_name='org_postal_address',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    billing_address = models.ForeignKey(
        'OrganisationAddress',
        related_name='org_billing_address',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    def upload_identification(self, request):
        with transaction.atomic():
            self.identification = request.data.dict()['identification']
            self.save()

    def __str__(self):
        return self.name


class OrganisationAddress(BaseAddress):
    organisation = models.ForeignKey(Organisation, null=True, blank=True, related_name='adresses')

    class Meta:
        verbose_name_plural = 'organisation addresses'
        unique_together = ('organisation', 'hash')


class ProfileListener(object):
    """
    Event listener for Profile

    """
    @staticmethod
    @receiver(post_delete, sender=Profile)
    def _post_delete(sender, instance, **kwargs):
        # delete from email identity, and social auth
        if instance.user.email == instance.email:
            # profile's email is user's email, return
            return

        # delete the profile's email from email identity and social auth
        EmailIdentity.objects.filter(email=instance.email, user=instance.user).delete()
        UserSocialAuth.objects.filter(provider="email", uid=instance.email, user=instance.user).delete()

    @staticmethod
    @receiver(pre_save, sender=Profile)
    def _pre_save(sender, instance, **kwargs):
        if not hasattr(instance, "auth_identity"):
            # not triggered by user.
            return

        if instance.pk:
            original_instance = Profile.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Profile)
    def _post_save(sender, instance, **kwargs):
        if not hasattr(instance, "auth_identity"):
            # not triggered by user.
            return

        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        auth_identity = getattr(instance, "auth_identity")
        if auth_identity:
            # add email to email identity and social auth if not exist
            EmailIdentity.objects.get_or_create(email=instance.email, user=instance.user)
            if not UserSocialAuth.objects.filter(user=instance.user, provider="email", uid=instance.email).exists():
                user_social_auth = UserSocialAuth.create_social_auth(instance.user, instance.email, 'email')
                user_social_auth.extra_data = {'email': [instance.email]}
                user_social_auth.save()

        if original_instance and (original_instance.email != instance.email or not auth_identity):
            # delete the profile's email from email identity and social auth
            EmailIdentity.objects.filter(email=original_instance.email, user=original_instance.user).delete()
            UserSocialAuth.objects.filter(provider="email", uid=original_instance.email, user=original_instance.user).delete()

        if not original_instance:
            address = instance.postal_address
            try:
                # Check if the user has the same profile address
                # Check if there is a user address
                oscar_add = UserAddress.objects.get(
                    line1=address.line1,
                    line2=address.line2,
                    line3=address.line3,
                    line4=address.locality,
                    state=address.state,
                    postcode=address.postcode,
                    country=Country.objects.get(iso_3166_1_a2=address.country),
                    user=instance.user
                )
                if not address.oscar_address:
                    address.oscar_address = oscar_add
                    address.save()
                elif address.oscar_address.id != oscar_add.id:
                    address.oscar_address = oscar_add
                    address.save()
            except UserAddress.DoesNotExist:
                oscar_address = UserAddress.objects.create(
                    line1=address.line1,
                    line2=address.line2,
                    line3=address.line3,
                    line4=address.locality,
                    state=address.state,
                    postcode=address.postcode,
                    country=Country.objects.get(iso_3166_1_a2=address.country),
                    user=instance.user
                )
                address.oscar_address = oscar_address
                address.save()
        # Clear out unused addresses
        # EmailUser can have address that is not linked with profile, hence the exclude
        ''' This functionality no longer in use due to more than just
        profile objects using the UserAddresses
        user = instance.user
        user_addr = Address.objects.filter(user=user)
        for u in user_addr:
            if not u.profiles.all() \
                and not u in (user.postal_address, user.residential_address, user.billing_address):
                u.oscar_address.delete()
                u.delete()'''


class EmailIdentityListener(object):
    """
    Event listener for EmailIdentity
    """
    @staticmethod
    @receiver(post_clean, sender=Profile)
    def _profile_post_clean(sender, instance, **kwargs):
        if instance.email:
            if EmailIdentity.objects.filter(email=instance.email).exclude(user=instance.user).exists():
                # Email already used by other user in email identity.
                raise ValidationError("This email address is already associated with an existing account or profile;\
                  if this email address belongs to you, please contact the system administrator to request for the email address\
                  to be added to your account.")

    @staticmethod
    @receiver(post_clean, sender=EmailUser)
    def _emailuser_post_clean(sender, instance, **kwargs):
        if instance.email:
            if EmailIdentity.objects.filter(email=instance.email).exclude(user=instance).exists():
                # Email already used by other user in email identity.
                raise ValidationError("This email address is already associated with an existing account or profile;\
                  if this email address belongs to you, please contact the system administrator to request for the email address\
                  to be added to your account.")


class AddressListener(object):
    """
        Event listener for Address
    """
    @staticmethod
    @receiver(pre_save, sender=Address)
    def _pre_save(sender, instance, **kwargs):
        check_address = UserAddress(
            line1=instance.line1,
            line2=instance.line2,
            line3=instance.line3,
            line4=instance.locality,
            state=instance.state,
            postcode=instance.postcode,
            country=Country.objects.get(iso_3166_1_a2=instance.country),
            user=instance.user
        )
        if instance.pk:
            original_instance = Address.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)
            if original_instance.oscar_address is None:
                try:
                    check_address = UserAddress.objects.get(hash=check_address.generate_hash(), user=check_address.user)
                except UserAddress.DoesNotExist:
                    check_address.save()
                instance.oscar_address = check_address
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            try:
                check_address = UserAddress.objects.get(hash=check_address.generate_hash(), user=check_address.user)
            except UserAddress.DoesNotExist:
                check_address.save()
            instance.oscar_address = check_address

    @staticmethod
    @receiver(post_save, sender=Address)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if original_instance:
            oscar_address = original_instance.oscar_address
            try:
                if oscar_address is not None:
                    oscar_address.line1 = instance.line1
                    oscar_address.line2 = instance.line2
                    oscar_address.line3 = instance.line3
                    oscar_address.line4 = instance.locality
                    oscar_address.state = instance.state
                    oscar_address.postcode = instance.postcode
                    oscar_address.country = Country.objects.get(iso_3166_1_a2=instance.country)
                    oscar_address.save()
            except IntegrityError as e:
                if 'unique constraint' in e.message:
                    raise ValidationError('Multiple profiles cannot have the same address.')
                else:
                    raise


@python_2_unicode_compatible
class EmailUserReport(models.Model):
    hash = models.TextField(primary_key=True)
    occurence = models.IntegerField()
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
    dob = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=False, verbose_name="date of birth", help_text='')

    def __str__(self):
        return 'Given Name(s): {}, Last Name: {}, DOB: {}, Occurence: {}'.format(
            self.first_name, self.last_name, self.dob, self.occurence
        )

    class Meta:
        managed = False
        db_table = 'accounts_emailuser_report_v'
