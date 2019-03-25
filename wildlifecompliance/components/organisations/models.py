from __future__ import unicode_literals

from django.db import models, transaction
from django.contrib.sites.models import Site
from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser, Document, RevisionedMixin
from wildlifecompliance.components.main.models import UserAction, CommunicationsLogEntry
from wildlifecompliance.components.organisations.utils import random_generator, get_officer_email_list
from wildlifecompliance.components.organisations.emails import (
    send_organisation_request_accept_email_notification,
    send_organisation_request_amendment_requested_email_notification,
    send_organisation_link_email_notification,
    send_organisation_unlink_email_notification,
    send_organisation_contact_adminuser_email_notification,
    send_organisation_contact_user_email_notification,
    send_organisation_contact_suspend_email_notification,
    send_organisation_reinstate_email_notification,
    send_organisation_contact_decline_email_notification,
    send_organisation_request_decline_email_notification,
    send_organisation_request_email_notification,
    send_organisation_request_link_email_notification,
    send_organisation_request_decline_admin_email_notification,
    send_organisation_request_accept_admin_email_notification,
    send_organisation_id_upload_email_notification,
    send_organisation_contact_consultant_email_notification,
)


@python_2_unicode_compatible
class Organisation(models.Model):
    organisation = models.ForeignKey(ledger_organisation)
    # TODO: business logic related to delegate changes.
    delegates = models.ManyToManyField(
        EmailUser,
        blank=True,
        through='UserDelegation',
        related_name='wildlifecompliance_organisations')
    admin_pin_one = models.CharField(max_length=50, blank=True)
    admin_pin_two = models.CharField(max_length=50, blank=True)
    user_pin_one = models.CharField(max_length=50, blank=True)
    user_pin_two = models.CharField(max_length=50, blank=True)

    class Meta:
        app_label = 'wildlifecompliance'

    def __str__(self):
        return str(self.organisation)

    def log_user_action(self, action, request):
        return OrganisationAction.log_action(self, action, request.user)

    def validate_pins(self, pin1, pin2, request):
        val_admin = self.admin_pin_one == pin1 and self.admin_pin_two == pin2
        val_user = self.user_pin_one == pin1 and self.user_pin_two == pin2
        if val_admin:
            val = val_admin
            admin_flag = True
            role = OrganisationContact.ORG_CONTACT_ROLE_ADMIN
        elif val_user:
            val = val_user
            admin_flag = False
            role = OrganisationContact.ORG_CONTACT_ROLE_USER
        else:
            val = False
            return val

        self.add_user_contact(request.user, request, admin_flag, role)
        return val

    def add_user_contact(self, user, request, admin_flag, role):
        with transaction.atomic():

            OrganisationContact.objects.create(
                organisation=self,
                first_name=user.first_name,
                last_name=user.last_name,
                mobile_number=user.mobile_number,
                phone_number=user.phone_number,
                fax_number=user.fax_number,
                email=user.email,
                user_role=role,
                user_status='pending',
                is_admin=admin_flag

            )

            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_CONTACT_ADDED.format(
                    '{} {}({})'.format(
                        user.first_name,
                        user.last_name,
                        user.email)),
                request)

    def accept_user(self, user, request):
        with transaction.atomic():
            # try:
            #     UserDelegation.objects.get(organisation=self,user=user)
            #     raise ValidationError('This user has already been linked to {}'.format(str(self.organisation)))
            # except UserDelegation.DoesNotExist:
            delegate = UserDelegation.objects.create(
                organisation=self, user=user)

            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                org_contact.user_status = OrganisationContact.ORG_CONTACT_STATUS_ACTIVE
                org_contact.save()
            except OrganisationContact.DoesNotExist:
                pass

        # log linking
            self.log_user_action(
                OrganisationAction.ACTION_LINK.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            send_organisation_link_email_notification(
                user, request.user, self, request)

    def decline_user(self, user, request):
        try:
            org_contact = OrganisationContact.objects.get(
                organisation=self, email=user.email)
            org_contact.user_status = OrganisationContact.ORG_CONTACT_STATUS_DECLINED
            org_contact.save()
        except OrganisationContact.DoesNotExist:
            pass
        OrganisationContactDeclinedDetails.objects.create(
            officer=request.user,
            request=org_contact
        )

        # log linking
        self.log_user_action(
            OrganisationAction.ACTION_CONTACT_DECLINED.format(
                '{} {}({})'.format(
                    user.first_name,
                    user.last_name,
                    user.email)),
            request)
        send_organisation_contact_decline_email_notification(
            user, request.user, self, request)

    # def link_user(self, user, request, admin_flag):
    #     with transaction.atomic():
    #         try:
    #             UserDelegation.objects.get(organisation=self, user=user)
    #             raise ValidationError('This user has already been linked to {}'.format(str(self.organisation)))
    #         except UserDelegation.DoesNotExist:
    #             delegate = UserDelegation.objects.create(organisation=self, user=user)
    #         if self.has_no_admins and ajsdhflkajhsdflkjhasdlkjfh:
    #             role = 'organisation_admin'
    #             is_admin = True
    #         elif admin_flag:
    #             role = 'organisation_admin'
    #             is_admin = True
    #         else:
    #             role = 'organisation_user'
    #             is_admin = False
    #
    #         # Create contact person
    #         OrganisationContact.objects.create(
    #             organisation=self,
    #             first_name=user.first_name,
    #             last_name=user.last_name,
    #             mobile_number=user.mobile_number,
    #             phone_number=user.phone_number,
    #             fax_number=user.fax_number,
    #             email=user.email,
    #             user_role=role,
    #             user_status='pending',
    #             is_admin=is_admin
    #
    #         )
    #         # log linking
    #         self.log_user_action(OrganisationAction.ACTION_LINK.format(
    #             '{} {}({})'.format(delegate.user.first_name, delegate.user.last_name, delegate.user.email)), request)
    #         # send email
    #         send_organisation_link_email_notification(user, request.user, self, request)

    def accept_declined_user(self, user, request):
        with transaction.atomic():
            try:
                UserDelegation.objects.get(organisation=self, user=user)
                raise ValidationError(
                    'This user has already been linked to {}'.format(str(self.organisation)))
            except UserDelegation.DoesNotExist:
                delegate = UserDelegation.objects.create(
                    organisation=self, user=user)

            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                org_contact.user_status = OrganisationContact.ORG_CONTACT_STATUS_ACTIVE
                org_contact.save()
            except OrganisationContact.DoesNotExist:
                pass

            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_LINK.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            # send email
            send_organisation_link_email_notification(
                user, request.user, self, request)

    def relink_user(self, user, request):
        with transaction.atomic():
            try:
                UserDelegation.objects.get(organisation=self, user=user)
                raise ValidationError(
                    'This user has not yet been linked to {}'.format(str(self.organisation)))
            except UserDelegation.DoesNotExist:
                delegate = UserDelegation.objects.create(
                    organisation=self, user=user)
            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                org_contact.user_status = OrganisationContact.ORG_CONTACT_STATUS_ACTIVE
                org_contact.save()
            except OrganisationContact.DoesNotExist:
                pass
            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_MAKE_CONTACT_REINSTATE.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            # send email
            send_organisation_reinstate_email_notification(
                user, request.user, self, request)

    def unlink_user(self, user, request):
        with transaction.atomic():
            try:
                delegate = UserDelegation.objects.get(
                    organisation=self, user=user)
            except UserDelegation.DoesNotExist:
                raise ValidationError(
                    'This user is not a member of {}'.format(str(self.organisation)))
            # delete contact person
            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                if org_contact.user_role == OrganisationContact.ORG_CONTACT_ROLE_ADMIN:
                    org_contact.user_status = OrganisationContact.ORG_CONTACT_STATUS_UNLINKED
                    org_contact.save()
                    # delete delegate
                    delegate.delete()
                else:
                    org_contact.user_status = OrganisationContact.ORG_CONTACT_STATUS_UNLINKED
                    org_contact.save()
                    # delete delegate
                    delegate.delete()
            except OrganisationContact.DoesNotExist:
                pass

            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_UNLINK.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            # send email
            send_organisation_unlink_email_notification(
                user, request.user, self, request)

    def make_admin_user(self, user, request):
        with transaction.atomic():
            try:
                delegate = UserDelegation.objects.get(
                    organisation=self, user=user)
            except UserDelegation.DoesNotExist:
                raise ValidationError(
                    'This user is not a member of {}'.format(str(self.organisation)))
            # delete contact person
            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                org_contact.user_role = OrganisationContact.ORG_CONTACT_ROLE_ADMIN
                org_contact.is_admin = True
                org_contact.save()
            except OrganisationContact.DoesNotExist:
                pass
            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_MAKE_CONTACT_ADMIN.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            # send email
            send_organisation_contact_adminuser_email_notification(
                user, request.user, self, request)

    def make_user(self, user, request):
        with transaction.atomic():
            try:
                delegate = UserDelegation.objects.get(
                    organisation=self, user=user)
            except UserDelegation.DoesNotExist:
                raise ValidationError(
                    'This user is not a member of {}'.format(str(self.organisation)))
            # delete contact person
            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                org_contact.user_role = OrganisationContact.ORG_CONTACT_ROLE_USER
                org_contact.is_admin = False
                org_contact.save()
            except OrganisationContact.DoesNotExist:
                pass
            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_MAKE_CONTACT_USER.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            # send email
            send_organisation_contact_user_email_notification(
                user, request.user, self, request)

    def make_consultant(self, user, request):
        with transaction.atomic():
            try:
                delegate = UserDelegation.objects.get(
                    organisation=self, user=user)
            except UserDelegation.DoesNotExist:
                raise ValidationError(
                    'This user is not a member of {}'.format(str(self.organisation)))
            # add consultant
            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                org_contact.user_role = OrganisationContact.ORG_CONTACT_ROLE_CONSULTANT
                org_contact.is_admin = True
                org_contact.save()
            except OrganisationContact.DoesNotExist:
                pass
            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_MAKE_CONTACT_ADMIN.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            # send email
            send_organisation_contact_consultant_email_notification(
                user, request.user, self, request)

    def suspend_user(self, user, request):
        with transaction.atomic():
            try:
                delegate = UserDelegation.objects.get(
                    organisation=self, user=user)
            except UserDelegation.DoesNotExist:
                raise ValidationError(
                    'This user is not a member of {}'.format(str(self.organisation)))
            # delete contact person
            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                org_contact.user_status = OrganisationContact.ORG_CONTACT_STATUS_SUSPENDED
                org_contact.save()
            except OrganisationContact.DoesNotExist:
                pass
            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_MAKE_CONTACT_SUSPEND.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            # send email
            send_organisation_contact_suspend_email_notification(
                user, request.user, self, request)

    def reinstate_user(self, user, request):
        with transaction.atomic():
            try:
                delegate = UserDelegation.objects.get(
                    organisation=self, user=user)
            except UserDelegation.DoesNotExist:
                raise ValidationError(
                    'This user is not a member of {}'.format(str(self.organisation)))
            # delete contact person
            try:
                org_contact = OrganisationContact.objects.get(
                    organisation=self, email=delegate.user.email)
                org_contact.user_status = OrganisationContact.ORG_CONTACT_STATUS_ACTIVE
                org_contact.save()
            except OrganisationContact.DoesNotExist:
                pass
            # log linking
            self.log_user_action(
                OrganisationAction.ACTION_MAKE_CONTACT_REINSTATE.format(
                    '{} {}({})'.format(
                        delegate.user.first_name,
                        delegate.user.last_name,
                        delegate.user.email)),
                request)
            # send email
            send_organisation_reinstate_email_notification(
                user, request.user, self, request)

    def generate_pins(self):
        self.admin_pin_one = self._generate_pin()
        self.admin_pin_two = self._generate_pin()
        self.user_pin_one = self._generate_pin()
        self.user_pin_two = self._generate_pin()
        self.save()

    def _generate_pin(self):
        return random_generator()

    def send_organisation_request_link_notification(self, request):
        # Notify each Admin member of request to be linked to org.
        contacts = OrganisationContact.objects.filter(
            organisation_id=self.id,
            user_role=OrganisationContact.ORG_CONTACT_ROLE_ADMIN,
            user_status=OrganisationContact.ORG_CONTACT_STATUS_ACTIVE,
            is_admin=True)
        recipients = [c.email for c in contacts]
        send_organisation_request_link_email_notification(
            self, request, recipients)

    def send_organisation_id_upload_email_notification(self, request):
        # Notify reviewing internal officers of update to the organisation ID.
        officer_list = get_officer_email_list(self)
        contact_email = EmailUser.objects.filter(email=request.user).first()
        if officer_list:
            send_organisation_id_upload_email_notification(
                officer_list, self, contact_email, request)

    @staticmethod
    def existance(abn):
        exists = True
        org = None
        l_org = None
        try:
            try:
                l_org = ledger_organisation.objects.get(abn=abn)
            except ledger_organisation.DoesNotExist:
                exists = False
            if l_org:
                try:
                    org = Organisation.objects.get(organisation=l_org)
                except Organisation.DoesNotExist:
                    exists = False
            if exists:
                return {
                    'exists': exists,
                    'id': org.id,
                    'first_five': org.first_five}
            return {'exists': exists}

        except BaseException:
            raise

    @property
    def name(self):
        return self.organisation.name

    @property
    def abn(self):
        return self.organisation.abn

    @property
    def address(self):
        return self.organisation.postal_address

    @property
    def phone_number(self):
        return self.organisation.phone_number

    @property
    def email(self):
        return self.organisation.email

    @property
    def first_five(self):
        """
        :return: A string of names for the first five Administrator delegates.
        """
        _names = ''
        for user in OrganisationContact.objects.filter(
                organisation_id=self.id,
                user_role=OrganisationContact.ORG_CONTACT_ROLE_ADMIN,
                user_status=OrganisationContact.ORG_CONTACT_STATUS_ACTIVE,
                is_admin=True):
            _names += '{0} {1} '.format(user.first_name, user.last_name)

        return _names

    @property
    def has_no_admins(self):
        return self.contacts.filter(user_role=OrganisationContact.ORG_CONTACT_ROLE_ADMIN).count() < 1

    @property
    def can_contact_user_edit(self):
        """
        :return: True if the application is in one of the editable status.
        """
        org_contact = OrganisationContact.objects.get(
            organisation_id=self.id, first_name=request.user.first_name)

        return org_contact.is_admin \
            and org_contact.user_status == OrganisationContact.ORG_CONTACT_STATUS_ACTIVE \
            and org_contact.user_role == OrganisationContact.ORG_CONTACT_ROLE_ADMIN

    @property
    def can_user_edit(self, email):
        """
        :return: True if the application is in one of the editable status.
        """
        org_contact = OrganisationContact.objects.get(
            organisation_id=self.id, email=email)

        return org_contact.is_admin \
            and org_contact.user_status == OrganisationContact.ORG_CONTACT_STATUS_ACTIVE \
            and org_contact.user_role == OrganisationContact.ORG_CONTACT_ROLE_ADMIN


@python_2_unicode_compatible
class OrganisationContact(models.Model):
    ORG_CONTACT_STATUS_DRAFT = 'draft'
    ORG_CONTACT_STATUS_PENDING = 'pending'
    ORG_CONTACT_STATUS_ACTIVE = 'active'
    ORG_CONTACT_STATUS_DECLINED = 'declined'
    ORG_CONTACT_STATUS_UNLINKED = 'unlinked'
    ORG_CONTACT_STATUS_SUSPENDED = 'suspended'
    USER_STATUS_CHOICES = ((ORG_CONTACT_STATUS_DRAFT, 'Draft'),
                           (ORG_CONTACT_STATUS_PENDING, 'Pending'),
                           (ORG_CONTACT_STATUS_ACTIVE, 'Active'),
                           (ORG_CONTACT_STATUS_DECLINED, 'Declined'),
                           (ORG_CONTACT_STATUS_UNLINKED, 'Unlinked'),
                           (ORG_CONTACT_STATUS_SUSPENDED, 'Suspended'))
    ORG_CONTACT_ROLE_ADMIN = 'organisation_admin'
    ORG_CONTACT_ROLE_USER = 'organisation_user'
    ORG_CONTACT_ROLE_CONSULTANT = 'consultant'
    USER_ROLE_CHOICES = ((ORG_CONTACT_ROLE_ADMIN, 'Organisation Admin'),
                         (ORG_CONTACT_ROLE_USER, 'Organisation User'),
                         (ORG_CONTACT_ROLE_CONSULTANT, 'Consultant')
                         )
    user_status = models.CharField(
        'Status',
        max_length=40,
        choices=USER_STATUS_CHOICES,
        default=ORG_CONTACT_STATUS_DRAFT)
    user_role = models.CharField(
        'Role',
        max_length=40,
        choices=USER_ROLE_CHOICES,
        default=ORG_CONTACT_ROLE_USER)
    organisation = models.ForeignKey(Organisation, related_name='contacts')
    email = models.EmailField(blank=False)
    first_name = models.CharField(
        max_length=128,
        blank=False,
        verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
    phone_number = models.CharField(max_length=50, null=True, blank=True,
                                    verbose_name="phone number", help_text='')
    mobile_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="mobile number",
        help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True,
                                  verbose_name="fax number", help_text='')
    is_admin = models.BooleanField(default=False)

    class Meta:
        app_label = 'wildlifecompliance'
        unique_together = (('organisation', 'email'),)

    def __str__(self):
        return '{} {}'.format(self.last_name, self.first_name)

    @property
    def can_edit(self):
        """
        :return: True if the application is in one of the editable status.
        """
        return self.is_admin \
            and self.user_status == OrganisationContact.ORG_CONTACT_STATUS_ACTIVE \
            and self.user_role == OrganisationContact.ORG_CONTACT_ROLE_ADMIN

    @property
    def check_consultant(self):
        """
        :return: True if the application is in one of the editable status.
        """
        return self.user_status == OrganisationContact.ORG_CONTACT_STATUS_ACTIVE \
            and self.user_role == OrganisationContact.ORG_CONTACT_ROLE_CONSULTANT

    # def unlink_user(self,user,request):
    #     with transaction.atomic():
    #         try:
    #             delegate = UserDelegation.objects.get(organisation=self.organisation_id,user=user)
    #         except UserDelegation.DoesNotExist:
    #             raise ValidationError('This user is not a member of {}'.format(str(self.organisation_id)))

    #         # delete delegate
    #         delegate.delete()
    #         self.user_status ='unlinked'
    #         self.save()
    #         # org = Organisation.objects.get(id=self.organisation_id)
    #         # log linking
    #         # self.log_user_action(OrganisationContactAction.ACTION_UNLINK.format('{} {}({})'.format(user.first_name,user.last_name,user.email)),request)
    #         # send email
    #         send_organisation_unlink_email_notification(user,request.user,self,request)

    def log_user_action(self, action, request):
        return OrganisationContactAction.log_action(self, action, request.user)


class OrganisationContactAction(UserAction):
    ACTION_ORGANISATION_CONTACT_ACCEPT = "Accept request {}"
    ACTION_ORGANISATION_CONTACT_DECLINE = "Decline Request {}"
    ACTION_UNLINK = "Unlinked the user{}"

    @classmethod
    def log_action(cls, request, action, user):
        return cls.objects.create(
            request=request,
            who=user,
            what=str(action)
        )

    request = models.ForeignKey(
        OrganisationContact,
        related_name='action_logs')

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ['-when']


class OrganisationContactDeclinedDetails(models.Model):
    request = models.ForeignKey(OrganisationContact)
    officer = models.ForeignKey(EmailUser, null=False)
    # reason = models.TextField(blank=True)

    class Meta:
        app_label = 'wildlifecompliance'


class UserDelegation(models.Model):
    organisation = models.ForeignKey(Organisation)
    user = models.ForeignKey(EmailUser)

    class Meta:
        unique_together = (('organisation', 'user'),)
        app_label = 'wildlifecompliance'


class OrganisationAction(UserAction):
    ACTION_REQUEST_APPROVED = "Organisation Request {} Approved"
    ACTION_LINK = "Linked {}"
    ACTION_UNLINK = "Unlinked {}"
    ACTION_CONTACT_ADDED = "Added new contact {}"
    ACTION_CONTACT_DECLINED = "Declined contact {}"
    ACTION_MAKE_CONTACT_ADMIN = "Made contact Organisation Admin {}"
    ACTION_MAKE_CONTACT_USER = "Made contact Organisation User {}"
    ACTION_CONTACT_REMOVED = "Removed contact {}"
    ACTION_ORGANISATIONAL_DETAILS_SAVED_NOT_CHANGED = "Details saved without changes"
    ACTION_ORGANISATIONAL_DETAILS_SAVED_CHANGED = "Details saved with the following changes: \n{}"
    ACTION_ORGANISATIONAL_ADDRESS_DETAILS_SAVED_NOT_CHANGED = "Address Details saved without changes"
    ACTION_ORGANISATIONAL_ADDRESS_DETAILS_SAVED_CHANGED = "Addres Details saved with folowing changes: \n{}"
    ACTION_ORGANISATION_CONTACT_ACCEPT = "Accepted contact {}"
    ACTION_CONTACT_DECLINE = "Declined contact {}"
    ACTION_MAKE_CONTACT_SUSPEND = "Suspended contact {}"
    ACTION_MAKE_CONTACT_REINSTATE = "REINSTATED contact {}"
    ACTION_ID_UPDATE = "Organisation {} Identification Updated"

    organisation = models.ForeignKey(Organisation, related_name='action_logs')

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ['-when']

    @classmethod
    def log_action(cls, organisation, action, user):
        return cls.objects.create(
            organisation=organisation,
            who=user,
            what=str(action)
        )


class OrganisationLogEntry(CommunicationsLogEntry):
    organisation = models.ForeignKey(Organisation, related_name='comms_logs')

    def save(self, **kwargs):
        # save the request id if the reference not provided
        if not self.reference:
            self.reference = self.organisation.id
        super(OrganisationLogEntry, self).save(**kwargs)

    class Meta:
        app_label = 'wildlifecompliance'


class OrganisationRequest(models.Model):
    ORG_REQUEST_STATUS_WITH_ASSESSOR = 'with_assessor'
    ORG_REQUEST_STATUS_AMENDMENT_REQUESTED = 'amendment_requested'
    ORG_REQUEST_STATUS_APPROVED = 'approved'
    ORG_REQUEST_STATUS_DECLINED = 'declined'
    STATUS_CHOICES = (
        (ORG_REQUEST_STATUS_WITH_ASSESSOR, 'With Assessor'),
        (ORG_REQUEST_STATUS_AMENDMENT_REQUESTED, 'Amendment Requested'),
        (ORG_REQUEST_STATUS_APPROVED, 'Approved'),
        (ORG_REQUEST_STATUS_DECLINED, 'Declined')
    )
    ORG_REQUEST_ROLE_EMPLOYEE = 'employee'
    ORG_REQUEST_ROLE_CONSULTANT = 'consultant'
    ROLE_CHOICES = (
        (ORG_REQUEST_ROLE_EMPLOYEE, 'Employee'),
        (ORG_REQUEST_ROLE_CONSULTANT, 'Consultant')
    )
    name = models.CharField(max_length=128)
    abn = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='ABN')
    requester = models.ForeignKey(EmailUser)
    assigned_officer = models.ForeignKey(
        EmailUser,
        blank=True,
        null=True,
        related_name='org_request_assignee')
    identification = models.FileField(
        upload_to='wildlifecompliance/organisation/requests/%Y/%m/%d',
        null=True,
        blank=True)
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default=ORG_REQUEST_STATUS_WITH_ASSESSOR)
    role = models.CharField(
        max_length=100,
        choices=ROLE_CHOICES,
        default=ORG_REQUEST_ROLE_EMPLOYEE)
    lodgement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'wildlifecompliance'

    def accept(self, request):
        with transaction.atomic():
            self.status = OrganisationRequest.ORG_REQUEST_STATUS_APPROVED
            self.save()
            self.log_user_action(
                OrganisationRequestUserAction.ACTION_ACCEPT_REQUEST.format(
                    self.id), request)
            # Continue with remaining logic
            self.__accept(request)

    def __accept(self, request):
        from wildlifecompliance.components.applications.models import ActivityPermissionGroup

        # Check if orgsanisation exists in ledger
        ledger_org = None
        try:
            ledger_org = ledger_organisation.objects.get(abn=self.abn)
        except ledger_organisation.DoesNotExist:
            ledger_org = ledger_organisation.objects.create(
                name=self.name, abn=self.abn)
        # Create Organisation in wildlifecompliance
        org, created = Organisation.objects.get_or_create(
            organisation=ledger_org)
        # org.generate_pins()
        # Link requester to organisation
        delegate = UserDelegation.objects.create(
            user=self.requester, organisation=org)
        # log who approved the request
        # org.log_user_action(OrganisationAction.ACTION_REQUEST_APPROVED.format(self.id),request)
        # log who created the link
        org.log_user_action(
            OrganisationAction.ACTION_LINK.format(
                '{} {}({})'.format(
                    delegate.user.first_name,
                    delegate.user.last_name,
                    delegate.user.email)),
            request)

        if self.role == OrganisationRequest.ORG_REQUEST_ROLE_CONSULTANT:
            role = OrganisationContact.ORG_CONTACT_ROLE_CONSULTANT
        else:
            role = OrganisationContact.ORG_CONTACT_ROLE_ADMIN
        # Create contact person

        OrganisationContact.objects.create(
            organisation=org,
            first_name=self.requester.first_name,
            last_name=self.requester.last_name,
            mobile_number=self.requester.mobile_number,
            phone_number=self.requester.phone_number,
            fax_number=self.requester.fax_number,
            email=self.requester.email,
            user_role=role,
            user_status=OrganisationContact.ORG_CONTACT_STATUS_ACTIVE,
            is_admin=True

        )

        # send email to requester
        send_organisation_request_accept_email_notification(self, org, request)
        # Notify other Organisation Access Group members of acceptance.
        groups = ActivityPermissionGroup.objects.filter(
            permissions__codename='organisation_access_request'
        )
        for group in groups:
            recipients = [member.email for member in group.members.exclude(
                          email=request.user.email)]
            if recipients:
                send_organisation_request_accept_admin_email_notification(
                    self, request, recipients)

    def amendment_request(self, request):
        with transaction.atomic():
            self.status = OrganisationRequest.ORG_REQUEST_STATUS_AMENDMENT_REQUESTED
            self.save()
            self.log_user_action(
                OrganisationRequestUserAction.ACTION_AMENDMENT_REQUEST.format(
                    self.id), request)
            # Continue with remaining logic
            self.__amendment_request(request)

    def __amendment_request(self, request):
        # Check if orgsanisation exists in ledger
        ledger_org = None
        try:
            ledger_org = ledger_organisation.objects.get(abn=self.abn)
        except ledger_organisation.DoesNotExist:
            ledger_org = ledger_organisation.objects.create(
                name=self.name, abn=self.abn)
        # Create Organisation in wildlifecompliance
        org, created = Organisation.objects.get_or_create(
            organisation=ledger_org)
        # send email to original requester
        send_organisation_request_amendment_requested_email_notification(
            self, org, request)

    def reupload_identification_amendment_request(self, request):
        with transaction.atomic():
            self.status = OrganisationRequest.ORG_REQUEST_STATUS_WITH_ASSESSOR
            self.identification = request.data.dict()['identification']
            self.save()
            self.log_user_action(
                OrganisationRequestUserAction.ACTION_REUPLOAD_IDENTIFICATION_AMENDMENT_REQUEST.format(
                    self.id), request)
            # Continue with remaining logic
            self.__reupload_identification_amendment_request(request)

    def __reupload_identification_amendment_request(self, request):
        # Check if orgsanisation exists in ledger
        ledger_org = None
        try:
            ledger_org = ledger_organisation.objects.get(abn=self.abn)
        except ledger_organisation.DoesNotExist:
            pass  # should never happen
            #ledger_org = ledger_organisation.objects.create(name=self.name, abn=self.abn)
        # Create Organisation in wildlifecompliance
        org = Organisation.objects.get(organisation=ledger_org)
        # send email to original requester
        # TODO:
        # send_organisation_request_amendment_requested_email_notification(self,
        # org, request)

    def assign_officer(self, user, request):
        with transaction.atomic():
            self.assigned_officer = user
            self.save()
            self.log_user_action(
                OrganisationRequestUserAction.ACTION_ASSIGN_TO.format(
                    user.get_full_name()), request)

    def unassign_officer(self, request):
        with transaction.atomic():
            self.assigned_officer = None
            self.save()
            self.log_user_action(
                OrganisationRequestUserAction.ACTION_UNASSIGN, request)

    def decline(self, request):
        from wildlifecompliance.components.applications.models import ActivityPermissionGroup

        with transaction.atomic():
            self.status = OrganisationRequest.ORG_REQUEST_STATUS_DECLINED
            self.save()
            OrganisationRequestDeclinedDetails.objects.create(
                officer=request.user,
                reason=OrganisationRequest.ORG_REQUEST_STATUS_DECLINED,
                request=self
            )
            self.log_user_action(
                OrganisationRequestUserAction.ACTION_DECLINE_REQUEST.format(
                    '{} {}({})'.format(
                        request.user.first_name,
                        request.user.last_name,
                        request.user.email)),
                request)
            send_organisation_request_decline_email_notification(self, request)
            # Notify other members of organisation access group of decline.
            groups = ActivityPermissionGroup.objects.filter(
                permissions__codename='organisation_access_request'
            )
            for group in groups:
                recipients = [member.email for member in group.members.exclude(
                              email=request.user.email)]
                if recipients:
                    send_organisation_request_decline_admin_email_notification(
                        self, request, recipients)

    def send_organisation_request_email_notification(self, request):
        from wildlifecompliance.components.applications.models import ActivityPermissionGroup

        # user submits a new organisation request
        # send email to organisation access group
        groups = ActivityPermissionGroup.objects.filter(
            permissions__codename='organisation_access_request'
        )
        for group in groups:
            org_access_recipients = [member.email for member in group.members]
            if org_access_recipients:
                send_organisation_request_email_notification(
                    self, request, org_access_recipients)

    def log_user_action(self, action, request):
        return OrganisationRequestUserAction.log_action(
            self, action, request.user)


class OrganisationRequestUserAction(UserAction):
    ACTION_LODGE_REQUEST = "Lodge request {}"
    ACTION_ASSIGN_TO = "Assign to {}"
    ACTION_UNASSIGN = "Unassign"
    ACTION_ACCEPT_REQUEST = "Accept request {}"
    ACTION_AMENDMENT_REQUEST = "Amendment request {}"
    ACTION_REUPLOAD_IDENTIFICATION_AMENDMENT_REQUEST = "Reupload identification amendment request {}"
    ACTION_DECLINE_REQUEST = "Decline request {}"
    # Assessors
    ACTION_CONCLUDE_REQUEST = "Conclude request {}"

    @classmethod
    def log_action(cls, request, action, user):
        return cls.objects.create(
            request=request,
            who=user,
            what=str(action)
        )

    request = models.ForeignKey(
        OrganisationRequest,
        related_name='action_logs')

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ['-when']


class OrganisationRequestDeclinedDetails(models.Model):
    request = models.ForeignKey(OrganisationRequest)
    officer = models.ForeignKey(EmailUser, null=False)
    reason = models.TextField(blank=True)

    class Meta:
        app_label = 'wildlifecompliance'


class OrganisationRequestLogEntry(CommunicationsLogEntry):
    request = models.ForeignKey(OrganisationRequest, related_name='comms_logs')

    def save(self, **kwargs):
        # save the request id if the reference not provided
        if not self.reference:
            self.reference = self.request.id
        super(OrganisationRequestLogEntry, self).save(**kwargs)

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ['-created']
