from __future__ import unicode_literals

import os

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_delete,pre_save,post_save

from reversion import revisions
from django_countries.fields import CountryField
from django.template.defaultfilters import default

from social.apps.django_app.default.models import UserSocialAuth

from datetime import datetime

from ledger.accounts.signals import name_changed

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
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename

class DocumentListener(object):
    """
    Event listener for Document.

    """
    @staticmethod
    @receiver(post_delete, sender=Document)
    def _post_delete(sender, instance,**kwargs):
        # Pass false so FileField doesn't save the model.
        try:
            instance.file.delete(False)
        except:
            #if deleting file is failed, ignore.
            pass

    @staticmethod
    @receiver(pre_save, sender=Document)
    def _pre_save(sender, instance,**kwargs):
        if instance.pk:
            original_instance = Document.objects.get(pk = instance.pk)
            setattr(instance,"_original_instance",original_instance)
        elif hasattr(instance,"_original_instance"):
            delattr(instance,"_original_instance")

    @staticmethod
    @receiver(post_save, sender=Document)
    def _post_save(sender, instance,**kwargs):
        original_instance = getattr(instance,"_original_instance") if hasattr(instance,"_original_instance") else None
        if original_instance and original_instance.file and instance.file != original_instance.file:
            #file changed, delete the original file
            try:
                original_file.delete(False);    
            except:
                #if deleting file is failed, ignore.
                pass
            delattr(instance,"_original_instance")

@python_2_unicode_compatible
class Address(models.Model):
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
    state = models.CharField(max_length=255, choices=STATE_CHOICES, default='WA', blank=True)
    country = CountryField(default='AU')
    postcode = models.CharField(max_length=10)
    # A field only used for searching addresses.
    search_text = models.TextField(editable=False)

    def __str__(self):
        return self.summary

    class Meta:
        verbose_name_plural = 'addresses'

    def clean(self):
        # Strip all whitespace
        for field in ['line1', 'line2', 'line3',
                      'locality', 'state']:
            if self.__dict__[field]:
                self.__dict__[field] = self.__dict__[field].strip()

    def save(self, *args, **kwargs):
        self._update_search_text()
        super(Address, self).save(*args, **kwargs)

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
    email = models.EmailField(unique=True,blank=False)
    first_name = models.CharField(max_length=128, blank=False)
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

    identification = models.ForeignKey(Document, null=True, blank=True, on_delete=models.SET_NULL, related_name='identification_document')

    character_flagged = models.BooleanField(default=False)

    character_comments = models.TextField(blank=True)

    documents = models.ManyToManyField(Document)

    extra_data = JSONField(default=dict)

    objects = EmailUserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        if self.is_dummy_user:
            if self.organisation:
                return '{} {} ({})'.format(self.first_name,self.last_name, self.organisation)
            return '{} {}'.format(self.first_name,self.last_name)
        else:
            if self.organisation:
                return '{} ({})'.format(self.email, self.organisation)
            return '{}'.format(self.email)

    def get_full_name(self):
        full_name = '{} {}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_full_name_dob(self):
        full_name_dob = '{} {} ({})'.format(self.first_name, self.last_name, self.dob.strftime('%d/%m/%Y'))
        return full_name_dob.strip()

    def get_short_name(self):
        if self.first_name:
            return self.first_name
        return self.email

    dummy_email_suffix = ".s058@ledger.dpaw.wa.gov.au"
    dummy_email_suffix_len = len(dummy_email_suffix)
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
        #use timestamp plus first name, last name to generate a unique id.
        uid = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return "{}.{}.{}{}".format(self.first_name,self.last_name,uid,self.dummy_email_suffix)

    @property
    def username(self):
        return self.email

class EmailUserListener(object):
    """
    Event listener for EmailUser

    """
    @staticmethod
    @receiver(post_delete, sender=EmailUser)
    def _post_delete(sender, instance,**kwargs):
        #delete the profile's email from email identity and social auth
        if not instance.is_dummy_user:
            EmailIdentity.objects.filter(email=instance.email,user=instance).delete()
            UserSocialAuth.objects.filter(provider="email",uid=instance.email,user=instance).delete()
        
    @staticmethod
    @receiver(pre_save, sender=EmailUser)
    def _pre_save(sender, instance,**kwargs):
        if instance.pk :
            original_instance = EmailUser.objects.get(pk = instance.pk)
            setattr(instance,"_original_instance",original_instance)
        elif hasattr(instance,"_original_instance"):
            delattr(instance,"_original_instance")

    @staticmethod
    @receiver(post_save, sender=EmailUser)
    def _post_save(sender, instance,**kwargs):
        original_instance = getattr(instance,"_original_instance") if hasattr(instance,"_original_instance") else None
        #add user's email to email identity and social auth if not exist
        if not instance.is_dummy_user:
            identity, created = EmailIdentity.objects.get_or_create(email=instance.email, user=instance)
            if not UserSocialAuth.objects.filter(user=instance,provider="email",uid=instance.email).exists():
                user_social_auth = UserSocialAuth.create_social_auth(instance, instance.email, 'email')
                user_social_auth.extra_data = {'email': [instance.email]}
                user_social_auth.save()

        if original_instance and original_instance.email != instance.email:
            if not original_instance.is_dummy_user:
                #delete the user's email from email identity and social auth
                EmailIdentity.objects.filter(email=original_instance.email,user=original_instance).delete()
                UserSocialAuth.objects.filter(provider="email",uid=original_instance.email,user=original_instance).delete()
            #update profile's email if profile's email is original email
            Profile.objects.filter(email=original_instance.email,user=instance).update(email=instance.email)

        if original_instance and any([original_instance.first_name != instance.first_name,original_instance.last_name != instance.last_name]):
            #user changed first name or last name, send a named_changed signal.
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
        return revisions.get_for_object(self).last().revision.date_created

    @property
    def modified_date(self):
        return revisions.get_for_object(self).first().revision.date_created

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Profile(RevisionedMixin):
    user = models.ForeignKey(EmailUser, verbose_name='User')
    name = models.CharField('Display Name', max_length=100, help_text='e.g Personal, Work, University, etc')
    email = models.EmailField('Email')
    postal_address = models.ForeignKey(Address, verbose_name='Postal Address', on_delete=models.PROTECT)
    institution = models.CharField('Institution', max_length=200, blank=True, default='', help_text='e.g. Company Name, Tertiary Institution, Government Department, etc')


    @property
    def is_auth_identity(self):
        """
        Return True if the email is an email identity; otherwise return False.
        """
        if not self.email: 
            return False;

        if not hasattr(self,"_auth_identity"):
            self._auth_identity = EmailIdentity.objects.filter(user=self.user,email=self.email).exists()

        return self._auth_identity

    def __str__(self):
        if len(self.name) > 0:
            return '{} ({})'.format(self.name, self.email)
        else:
            return '{}'.format(self.email)



class ProfileListener(object):
    """
    Event listener for Profile

    """
    @staticmethod
    @receiver(post_delete, sender=Profile)
    def _post_delete(sender, instance,**kwargs):
        # delete from email identity, and social auth
        if instance.user.email == instance.email:
            #profile's email is user's email, return
            return

        #delete the profile's email from email identity and social auth
        EmailIdentity.objects.filter(email=instance.email,user=instance.user).delete()
        UserSocialAuth.objects.filter(provider="email",uid=instance.email,user=instance.user).delete()
        
    @staticmethod
    @receiver(pre_save, sender=Profile)
    def _pre_save(sender, instance,**kwargs):
        if not hasattr(instance,"auth_identity"):
            #not triggered by user.
            return

        if instance.pk :
            original_instance = Profile.objects.get(pk = instance.pk)
            setattr(instance,"_original_instance",original_instance)
        elif hasattr(instance,"_original_instance"):
            delattr(instance,"_original_instance")

    @staticmethod
    @receiver(post_save, sender=Profile)
    def _post_save(sender, instance,**kwargs):
        if not hasattr(instance,"auth_identity"):
            #not triggered by user.
            return

        original_instance = getattr(instance,"_original_instance") if hasattr(instance,"_original_instance") else None
        auth_identity = getattr(instance,"auth_identity")
        if auth_identity == True:
            #add email to email identity and social auth if not exist
            identity, created = EmailIdentity.objects.get_or_create(email=instance.email, user=instance.user)
            if not UserSocialAuth.objects.filter(user=instance.user,provider="email",uid=instance.email).exists():
                user_social_auth = UserSocialAuth.create_social_auth(instance.user, instance.email, 'email')
                user_social_auth.extra_data = {'email': [instance.email]}
                user_social_auth.save()

        if original_instance and (original_instance.email != instance.email or not auth_identity):
            #delete the profile's email from email identity and social auth
            EmailIdentity.objects.filter(email=original_instance.email,user=original_instance.user).delete()
            UserSocialAuth.objects.filter(provider="email",uid=original_instance.email,user=original_instance.user).delete()

