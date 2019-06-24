from __future__ import unicode_literals
from django.db import models, transaction
from django.db.models.signals import post_save
from django.contrib.postgres.fields.jsonb import JSONField
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import FieldError, ValidationError
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.payments.invoice.models import Invoice
from ledger.checkout.utils import calculate_excl_gst
from wildlifecompliance.components.main.utils import checkout, flush_checkout_session
from wildlifecompliance.components.returns.utils_schema import Schema
from wildlifecompliance.components.applications.models import ApplicationCondition, Application
from wildlifecompliance.components.main.models import CommunicationsLogEntry, UserAction
from wildlifecompliance.components.returns.email import send_external_submit_email_notification, \
                                                        send_return_accept_email_notification, \
                                                        send_sheet_transfer_email_notification
import ast
import logging

logger = logging.getLogger(__name__)


def template_directory_path(instance, filename):
    """
    Static location for Returns template.
    :param instance: Request.
    :param filename: Name of file.
    :return: file path.
    """
    return 'wildlifecompliance/returns/template/{0}'.format(filename)


class ReturnType(models.Model):
    """
    A definition to identify the format used to facilitate Return.
    """
    FORMAT_SHEET = 'sheet'
    FORMAT_QUESTION = 'question'
    FORMAT_DATA = 'data'
    FORMAT_CHOICES = (
        (FORMAT_SHEET, 'Sheet'),
        (FORMAT_QUESTION, 'Question'),
        (FORMAT_DATA, 'Data')
    )
    name = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True, max_length=256)
    data_descriptor = JSONField()
    data_format = models.CharField(
        'Data format',
        max_length=30,
        choices=FORMAT_CHOICES,
        default=FORMAT_DATA)
    # data_template is only used by ReturnData Format for upload.
    data_template = models.FileField(upload_to=template_directory_path, null=True, blank=True)
    fee_required = models.BooleanField(default=False)
    # fee_amount is a base amount required for the Return Type.
    fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default='0')
    # fee_name is an optional field for fee and can be used to correspond to JSON property.
    fee_name = models.CharField(null=True, blank=True, max_length=50)
    replaced_by = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)

    class Meta:
        app_label = 'wildlifecompliance'
        unique_together = ('name', 'version')

    @property
    def resources(self):
        return self.data_descriptor.get('resources', [])

    def get_resource_by_name(self, name):
        for resource in self.resources:
            if resource.get('name') == name:
                return resource
        return None

    def get_schema_by_name(self, name):
        resource = self.get_resource_by_name(name)
        return resource.get('schema', {}) if resource else None

    def __str__(self):
        return '{0} - v{1}'.format(self.name, self.version)


class Return(models.Model):
    """
    A number of requirements relating to a Licence condition recorded during the Licence period.
    """
    RETURN_PROCESSING_STATUS_DUE = 'due'
    RETURN_PROCESSING_STATUS_OVERDUE = 'overdue'
    RETURN_PROCESSING_STATUS_DRAFT = 'draft'
    RETURN_PROCESSING_STATUS_FUTURE = 'future'
    RETURN_PROCESSING_STATUS_WITH_CURATOR = 'with_curator'
    RETURN_PROCESSING_STATUS_ACCEPTED = 'accepted'
    RETURN_PROCESSING_STATUS_PAYMENT = 'payment'
    PROCESSING_STATUS_CHOICES = (
        (RETURN_PROCESSING_STATUS_DUE, 'Due'),
        (RETURN_PROCESSING_STATUS_OVERDUE, 'Overdue'),
        (RETURN_PROCESSING_STATUS_DRAFT, 'Draft'),
        (RETURN_PROCESSING_STATUS_FUTURE, 'Future'),
        (RETURN_PROCESSING_STATUS_WITH_CURATOR, 'With Curator'),
        (RETURN_PROCESSING_STATUS_ACCEPTED, 'Accepted'),
        (RETURN_PROCESSING_STATUS_PAYMENT, 'Awaiting Payment')
    )
    RETURN_CUSTOMER_STATUS_DUE = 'due'
    RETURN_CUSTOMER_STATUS_OVERDUE = 'overdue'
    RETURN_CUSTOMER_STATUS_DRAFT = 'draft'
    RETURN_CUSTOMER_STATUS_FUTURE = 'future'
    RETURN_CUSTOMER_STATUS_UNDER_REVIEW = 'under_review'
    RETURN_CUSTOMER_STATUS_ACCEPTED = 'accepted'

    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    application = models.ForeignKey(Application, related_name='returns_application')
    licence = models.ForeignKey(
        'wildlifecompliance.WildlifeLicence',
        related_name='returns_licence')
    due_date = models.DateField()
    processing_status = models.CharField(
        choices=PROCESSING_STATUS_CHOICES,
        max_length=20,
        default=RETURN_PROCESSING_STATUS_FUTURE)
    assigned_to = models.ForeignKey(
        EmailUser,
        related_name='returns_curator',
        null=True,
        blank=True)
    condition = models.ForeignKey(
        ApplicationCondition,
        blank=True,
        null=True,
        related_name='returns_condition',
        on_delete=models.SET_NULL)
    lodgement_date = models.DateTimeField(blank=True, null=True)
    submitter = models.ForeignKey(
        EmailUser,
        blank=True,
        null=True,
        related_name='returns_submitter')
    reminder_sent = models.BooleanField(default=False)
    post_reminder_sent = models.BooleanField(default=False)
    return_type = models.ForeignKey(ReturnType, null=True)
    nil_return = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    return_fee = models.DecimalField(max_digits=8, decimal_places=2, default='0')

    class Meta:
        app_label = 'wildlifecompliance'

    # Append 'R' to Return id to generate Return lodgement number.
    def save(self, *args, **kwargs):
        super(Return, self).save(*args, **kwargs)
        if self.lodgement_number == '':
            new_lodgement_id = 'R{0:06d}'.format(self.pk)
            self.lodgement_number = new_lodgement_id
            self.save()

    @property
    def activity(self):
        return self.application.activity

    @property
    def title(self):
        return self.application.title

    @property
    def holder(self):
        return self.application.applicant

    @property
    def resources(self):
        return self.return_type.data_descriptor.get('resources', [])

    @property
    def format(self):
        return self.return_type.data_format

    @property
    def template(self):
        """
        Return data spreadsheet template for uploading information.
        :return: spreadsheet template format.
        """
        return self.return_type.data_template.url if self.return_type.data_template else None

    @property
    def table(self):
        """
        Return data presented in table format with column headers.
        :return: formatted data.
        """
        if self.has_sheet:
            return self.sheet.table
        if self.has_data:
            return self.data.table
        if self.has_question:
            return self.question.table

        return []

    @property
    def sheet(self):
        """
        A Running sheet of Return data.
        :return: ReturnSheet with activity data for Licence species.
        """
        return ReturnSheet(self) if self.has_sheet else None

    @property
    def data(self):
        """
        Return data.
        :return: Details of activities relating to Licence species.
        """
        return ReturnData(self) if self.has_data else None

    @property
    def question(self):
        """
        Questionnaire of Return data.
        :return: Questionnaire on activities relating to Licence species.
        """
        return ReturnQuestion(self) if self.has_question else None

    @property
    def has_question(self):
        """
        Property defining if the Return is Question based.
        :return: Boolean
        """
        return True if self.format == ReturnType.FORMAT_QUESTION else False

    @property
    def has_data(self):
        """
        Property defining if the Return is Data based.
        :return: Boolean
        """
        return True if self.format == ReturnType.FORMAT_DATA else False

    @property
    def has_sheet(self):
        """
        Property defining if the Return is Running Sheet based.
        :return: Boolean
        """
        return True if self.format == ReturnType.FORMAT_SHEET else False

    @property
    def customer_status(self):
        """
        Property defining external status in relation to processing status.
        :return: External Status.
        """
        workflow_mapper = {
            self.RETURN_PROCESSING_STATUS_DUE: self.RETURN_CUSTOMER_STATUS_DUE,
            self.RETURN_PROCESSING_STATUS_OVERDUE: self.RETURN_CUSTOMER_STATUS_OVERDUE,
            self.RETURN_PROCESSING_STATUS_DRAFT: self.RETURN_CUSTOMER_STATUS_DRAFT,
            self.RETURN_PROCESSING_STATUS_FUTURE: self.RETURN_CUSTOMER_STATUS_FUTURE,
            self.RETURN_PROCESSING_STATUS_WITH_CURATOR: self.RETURN_CUSTOMER_STATUS_UNDER_REVIEW,
            self.RETURN_PROCESSING_STATUS_ACCEPTED: self.RETURN_CUSTOMER_STATUS_ACCEPTED,
            self.RETURN_PROCESSING_STATUS_PAYMENT: self.RETURN_CUSTOMER_STATUS_UNDER_REVIEW
        }

        return workflow_mapper.get(self.processing_status, self.RETURN_CUSTOMER_STATUS_FUTURE)

    @property
    def payment_status(self):
        """
        Property defining fee status for this Return.
        :return:
        """
        if self.return_fee == 0:
            return Invoice.PAYMENT_STATUS_NOT_REQUIRED
        else:
            if self.invoices.count() == 0:
                return Invoice.PAYMENT_STATUS_UNPAID
            else:
                try:
                    latest_invoice = Invoice.objects.get(reference=self.invoices.latest('id').invoice_reference)
                except Invoice.DoesNotExist:
                    return Invoice.PAYMENT_STATUS_UNPAID
                return latest_invoice.payment_status

    @property
    def return_fee_paid(self):
        return self.payment_status in [
            Invoice.PAYMENT_STATUS_NOT_REQUIRED,
            Invoice.PAYMENT_STATUS_PAID,
            Invoice.PAYMENT_STATUS_OVERPAID,
        ]

    @property
    def has_payment(self):
        """
        Property defining if payment is required for this Return.
        :return:
        """
        return True if self.payment_status != Invoice.PAYMENT_STATUS_NOT_REQUIRED else False

    @transaction.atomic
    def set_submitted(self, request):
        try:
            if self.processing_status == Return.RETURN_PROCESSING_STATUS_FUTURE\
                     or self.processing_status == Return.RETURN_PROCESSING_STATUS_DUE:
                self.processing_status = Return.RETURN_PROCESSING_STATUS_WITH_CURATOR
                self.submitter = request.user
                self.save()

            # code for amendment returns is still to be added, so
            # lodgement_date is set outside if statement
            self.lodgement_date = timezone.now()
            self.save()
            # this below code needs to be reviewed
            # self.save(version_comment='Return submitted:{}'.format(self.id))
            # self.application.save(version_comment='Return submitted:{}'.format(self.id))
            self.log_user_action(ReturnUserAction.ACTION_SUBMIT_REQUEST.format(self), request)
            send_external_submit_email_notification(request, self)
            # send_submit_email_notification(request,self)
        except BaseException:
            raise

    @transaction.atomic
    def accept(self, request):
        try:
            self.processing_status = Return.RETURN_PROCESSING_STATUS_ACCEPTED
            self.save()
            self.log_user_action(ReturnUserAction.ACTION_ACCEPT_REQUEST.format(self), request)
            send_return_accept_email_notification(self, request)
        except BaseException:
            raise

    @transaction.atomic
    def save_return_table(self, table_name, table_rows, request):
        """
        Persist Return Table of data to database.
        :param table_name:
        :param table_rows:
        :param request:
        :return:
        """
        try:
            return_table = ReturnTable.objects.get_or_create(
                name=table_name, ret=self)[0]
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in table_rows]
            ReturnRow.objects.bulk_create(return_rows)
            # log transaction
            self.log_user_action(ReturnUserAction.ACTION_SAVE_REQUEST.format(self), request)
        except BaseException:
            raise

    def log_user_action(self, action, request):
        return ReturnUserAction.log_action(self, action, request.user)

    def __str__(self):
        return self.lodgement_number


class ReturnListener(object):
    """
    Listener object signalling additional processing outside Return model.
    """
    @staticmethod
    @receiver(post_save, sender=Return)
    def post_create(sender, instance, created, **kwargs):
        if not created:
            return
        if instance.has_sheet:
            # create default species data for Return running sheets.
            instance.sheet.set_licence_species


class ReturnData(object):
    """
    Informational data of requirements supporting licence condition.
    """
    def __init__(self, a_return):
        self._return = a_return

    @property
    def table(self):
        """
        Table of return information presented in Grid format.
        :return: Grid formatted data.
        """
        tables = []
        for resource in self._return.return_type.resources:
            resource_name = resource.get('name')
            schema = Schema(resource.get('schema'))
            headers = []
            for f in schema.fields:
                header = {
                    "label": f.data['label'],
                    "name": f.data['name'],
                    "required": f.required,
                    "type": f.type.name,
                    "readonly": False,
                }
                if f.is_species:
                    header["species"] = f.species_type
                headers.append(header)
            table = {
                'name': resource_name,
                'label': resource.get('title', resource.get('name')),
                'type': 'grid',
                'headers': headers,
                'data': None
            }
            try:
                return_table = self._return.returntable_set.get(name=resource_name)
                rows = [
                    return_row.data for return_row in return_table.returnrow_set.all()]
                validated_rows = schema.rows_validator(rows)
                table['data'] = validated_rows
            except ReturnTable.DoesNotExist:
                result = {}
                results = []
                for field_name in schema.fields:
                    result[field_name.name] = {
                            'value': None
                    }
                results.append(result)
                table['data'] = results
            tables.append(table)

        return tables

    def store(self, request):
        """
        Save the current state of this Return Data.
        :param request:
        :return:
        """
        for key in request.data.keys():
            if key == "nilYes":
                self._return.nil_return = True
                self._return.comments = request.data.get('nilReason')
                self._return.save()
            if key == "nilNo":
                returns_tables = request.data.get('table_name')
                if self._is_post_data_valid(returns_tables.encode('utf-8'), request.data):
                    table_info = returns_tables.encode('utf-8')
                    table_rows = self._get_table_rows(table_info, request.data)
                    if table_rows:
                        self._return.save_return_table(table_info, table_rows, request)
                else:
                    raise FieldError('Enter data in correct format.')

    def build_table(self, rows):
        """
        Method to create and validate rows of data to the table schema without persisting. Used for
        Loading data from spreadsheets.
        :param rows: data to be formatted.
        :return: Array of tables.
        """
        tables = []
        for resource in self._return.return_type.resources:
            resource_name = resource.get('name')
            schema = Schema(resource.get('schema'))
            table = {
                'name': resource_name,
                'label': resource.get('title', resource.get('name')),
                'type': None,
                'headers': None,
                'data': None
            }
            try:
                validated_rows = schema.rows_validator(rows)
                table['data'] = validated_rows
            except AttributeError:
                result = {}
                results = []
                for field_name in schema.fields:
                    result[field_name.name] = {
                            'value': None
                    }
                results.append(result)
                table['data'] = results
            tables.append(table)

        return tables

    def _is_post_data_valid(self, tables_info, post_data):
        """
        Validates table data against the Schema for correct entry of data types.
        :param tables_info:
        :param post_data:
        :return:
        """
        table_rows = self._get_table_rows(tables_info, post_data)
        if len(table_rows) == 0:
            return False
        schema = Schema(self._return.return_type.get_schema_by_name(tables_info))
        if not schema.is_all_valid(table_rows):
            return False
        return True

    def _get_table_rows(self, table_name, post_data):
        """
        Builds a row of data taken from a table into a standard that can be consumed by the Schema.
        :param table_name:
        :param post_data:
        :return:
        """
        table_namespace = table_name + '::'
        # exclude fields defaulted from renderer. ie comment-field, deficiency-field (Application specific)
        excluded_field = ('-field')
        by_column = dict([(key.replace(table_namespace, ''), post_data.getlist(
            key)) for key in post_data.keys() if key.startswith(table_namespace) and not key.endswith(excluded_field)])
        # by_column is of format {'col_header':[row1_val, row2_val,...],...}
        num_rows = len(
            list(
                by_column.values())[0]) if len(
            by_column.values()) > 0 else 0
        rows = []
        for row_num in range(num_rows):
            row_data = {}
            for key, value in by_column.items():
                row_data[key] = value[row_num]
            # filter empty rows.
            is_empty = True
            for value in row_data.values():
                if len(value.strip()) > 0:
                    is_empty = False
                    break
            if not is_empty:
                rows.append(row_data)
        return rows

    def __str__(self):
        return self._return.lodgement_number


class ReturnQuestion(object):
    """
    Informational question of requirements supporting licence condition.
    """
    def __init__(self, a_return):
        self._return = a_return

    @property
    def table(self):
        """
        Table of return questions.
        :return: formatted data.
        """
        tables = []
        for resource in self._return.return_type.resources:
            resource_name = ReturnType.FORMAT_QUESTION
            schema = Schema(resource.get('schema'))
            headers = []
            for f in schema.fields:
                header = {
                    "label": f.data['label'],
                    "name": f.data['name'],
                    "required": f.required,
                    "type": f.type.name,
                    "readonly": False,
                }
                if f.is_species:
                    header["species"] = f.species_type
                headers.append(header)
            table = {
                'name': resource_name,
                'title': resource.get('title', resource.get('name')),
                'headers': headers,
                'data': None
            }
            try:
                return_table = self._return.returntable_set.get(name=resource_name)
                rows = [
                    return_row.data for return_row in return_table.returnrow_set.all()]
                table['data'] = rows
            except ReturnTable.DoesNotExist:
                result = {}
                results = []
                for field_name in schema.fields:
                    result[field_name.name] = {
                        'value': None
                    }
                results.append(result)
                table['data'] = results
            tables.append(table)
        return tables

    def store(self, request):
        """
        Save the current state of the Return.
        :param request:
        :return:
        """
        table_rows = self._get_table_rows(request.data)  # Nb: There is only ONE row where each Question is a header.
        self._return.save_return_table(ReturnType.FORMAT_QUESTION, table_rows, request)

    def _get_table_rows(self, _data):
        """
        Builds a row of data taken from the Request into a standard that can be saved.
        :param _data:
        :return:
        """
        by_column = dict([])  # by_column is of format {'col_header':[row1_val, row2_val,...],...}
        rows = []
        for key in _data.keys():
            by_column[key] = _data[key]
        rows.append(by_column)

        return rows

    def __str__(self):
        return self._return.lodgement_number


class ReturnSheet(object):
    """
    Informational Running Sheet of Species requirements supporting licence condition.
    """
    _DEFAULT_SPECIES = '0000000'

    _SHEET_SCHEMA = {"name": "sheet", "title": "Running Sheet of Return Data", "resources": [{"name":
                     "species_id", "path": "", "title": "Return Data for Specie", "schema": {"fields": [{"name":
                     "date", "type": "date", "format": "fmt:%d/%m/%Y", "constraints": {"required": True}}, {"name":
                     "activity", "type": "string", "constraints": {"required": True}}, {"name": "qty", "type":
                     "number", "constraints": {"required": True}}, {"name": "total", "type": "number",
                     "constraints": {"required": True}}, {"name": "licence", "type": "string"}, {"name": "comment",
                     "type": "string"}, {"name": "transfer", "type": "string"}]}}]}

    _NO_ACTIVITY = {"echo": 1, "totalRecords": "0", "totalDisplayRecords": "0", "data": []}

    # todo: change activity id to a meaningful name
    _ACTIVITY_TYPES = {
        "SA01": {"label": "Stock", "auto": "false", "licence": "false", "pay": "false", "initial": ""},
        "SA02": {"label": "In through import", "auto": "false", "licence": "false", "pay": "false", "inward": ""},
        "SA03": {"label": "In through birth", "auto": "false", "licence": "false", "pay": "false", "inward": ""},
        "SA04": {"label": "In through transfer", "auto": "true", "licence": "false", "pay": "false", "inward": ""},
        "SA05": {"label": "Out through export", "auto": "false", "licence": "false", "pay": "false", "outward": ""},
        "SA06": {"label": "Out through death", "auto": "false", "licence": "false", "pay": "false", "outward": ""},
        "SA07": {"label": "Out through transfer other", "auto": "false", "licence": "true", "pay": "true", "outward": "SA04"},
        "SA08": {"label": "Out through transfer dealer", "auto": "false", "licence": "true", "pay": "false", "outward": "SA04"},
        "0": {"label": "", "auto": "false", "licence": "false", "pay": "false", "initial": ""}}

    def __init__(self, a_return):
        self._return = a_return
        self._return.return_type.data_descriptor = self._SHEET_SCHEMA
        self._species_list = []
        self._table = {'data': None}
        # build list of currently added Species.
        self._species = self._DEFAULT_SPECIES
        for _species in ReturnTable.objects.filter(ret=a_return):
            self._species_list.append(_species.name)
            self._species = _species.name

    @staticmethod
    def set_licence_species(the_return):
        """
        Sets the species from the licence for the current Running Sheet.
        :return:
        """
        _data = []
        # TODO: create default entries for each species on the licence.
        # TODO: Each species has a defaulted Stock Activity (0 Totals).
        '''
        new_sheet = the_return.sheet
        for species in the_return.licence.species_list:
            try:
                _data = {''}
                table_rows = new_sheet._get_table_rows(_data)
                self._return.save_return_table(species, table_rows, request)
            except AttributeError:
                continue
        '''
        pass

    @property
    def table(self):
        """
        Running Sheet Table of data for Species. Defaults to a Species on the Return if exists.
        :return: formatted data.
        """
        return self._get_activity(self._species)['data']

    @property
    def species(self):
        """
        Species type associated with this Running Sheet of Activities.
        :return:
        """
        return self._species

    @property
    def species_list(self):
        """
        List of Species available with Running Sheet of Activities.
        :return: List of Species.
        """
        return self._species_list

    @property
    def activity_list(self):
        """
        List of stock movement activities applicable for Running Sheet.
        Format: "SA01": {"label": "Stock", "auto": "false", "licence": "false", "pay": "false", "outward": "SA04"}
        Label: Activity Description.
        Auto: Flag indicating automated activity.
        Licence: Flag indicating licence required for activity.
        Pay: Flag indicating payment required for activity.
        Inward/Outward: Transfer type with Activity Type code for outward transfer.
        :return: List of Activities applicable for Running Sheet.
        """
        return self._ACTIVITY_TYPES

    # todo: more generic method name for payment transfer
    @property
    def process_transfer_fee_payment(self, request):
        from ledger.payments.models import BpointToken
        #if self.return_fee_paid:
        #    return True

        application = self.application
        applicant = application.proxy_applicant if application.proxy_applicant else application.submitter
        card_owner_id = applicant.id
        card_token = BpointToken.objects.filter(user_id=card_owner_id).order_by('-id').first()
        if not card_token:
            logger.error("No card token found for user: %s" % card_owner_id)
            return False

        product_lines = []
        return_submission = u'Transfer of stock for {} Return {}'.format(
            u'{} {}'.format(applicant.first_name, applicant.last_name), application.lodgement_number)
        product_lines.append({
            'ledger_description': '{}'.format(self._return.id),
            'quantity': 1,
            'price_incl_tax': str(self._return.return_fee),
            'price_excl_tax': str(calculate_excl_gst(self.licence_fee)),
            'oracle_code': ''
        })
        checkout(
            request, application, lines=product_lines,
            invoice_text=return_submission,
            internal=True,
            add_checkout_params={
                'basket_owner': request.user.id,
                'payment_method': 'card',
                'checkout_token': card_token.id,
            }
        )
        try:
            invoice_ref = request.session['checkout_invoice']
        except KeyError:
            logger.error("No invoice reference generated for Activity ID: %s" % self.licence_activity_id)
            return False
        ReturnInvoice.objects.get_or_create(
            invoice_return=self,
            invoice_reference=invoice_ref
        )
        flush_checkout_session(request.session)
        #return self.licence_fee_paid and send_activity_invoice_email_notification(application, self, invoice_ref, request)
        return self.licence_fee_paid

    def store(self, request):
        """
        Save the current state of this Return Sheet.
        :param request:
        :return:
        """
        for species in self.species_list:
            try:
                _data = request.data.get(species).encode('utf-8')
                _data = ast.literal_eval(_data)  # ast should convert list to tuple.
                table_rows = self._get_table_rows(_data)
                self._return.save_return_table(species, table_rows, request)
            except AttributeError:
                continue
        self._add_transfer_activity(request)

    def set_species(self, _species):
        """
        Sets the species for the current Running Sheet.
        :param _species:
        :return:
        """
        self._species = _species
        #self._species_list.add(_species)

    def get_species(self):
        """
        Gets the species for the current Running Sheet.
        :return:
        """
        return self._species

    def is_valid_transfer(self, request):
        """
        Validate transfer request details.
        :param request:
        :return:
        """
        is_valid = True
        if not request.data.get('transfer'):
            return False
        _data = request.data.get('transfer').encode('utf-8')
        _transfers = ast.literal_eval(_data)
        _licence = _transfers['licence']
        is_valid = False if not is_valid else self._is_valid_transfer_licence(_licence)
        #is_valid = False if not is_valid else self._is_valid_transfer_quantity(request)

        return is_valid

    def _get_activity(self, _species_id):
        """
        Get Running Sheet activity for the movement of Species stock.
        :return: formatted data {'name': 'speciesId', 'data': [{'date': '2019/01/23', 'activity': 'SA01', ..., }]}
        """
        _row = {}
        _result = []
        self._species = _species_id
        for resource in self._return.return_type.resources:
            _resource_name = _species_id
            _schema = Schema(resource.get('schema'))
            try:
                _return_table = self._return.returntable_set.get(name=_resource_name)
                rows = [_return_row.data for _return_row in _return_table.returnrow_set.all()]
                _validated_rows = _schema.rows_validator(rows)
                self._table['data'] = rows
                self._table['echo'] = 1
                self._table['totalRecords'] = str(rows.__len__())
                self._table['totalDisplayRecords'] = str(rows.__len__())
            except ReturnTable.DoesNotExist:
                self._table = self._NO_ACTIVITY

        return self._table

    def _get_table_rows(self, _data):
        """
        Gets the formatted row of data from Species data.
        :param _data:
        :return:
        """
        by_column = dict([])  # by_column is of format {'col_header':[row1_val, row2_val,...],...}
        key_values = []
        num_rows = 0
        if isinstance(_data, tuple):
            for key in _data[0].keys():
                for cnt in range(_data.__len__()):
                    key_values.append(_data[cnt][key])
                by_column[key] = key_values
                key_values = []
            num_rows = len(list(by_column.values())[0]) if len(by_column.values()) > 0 else 0
        else:
            for key in _data.keys():
                by_column[key] = _data[key]
            num_rows = num_rows + 1

        rows = []
        for row_num in range(num_rows):
            row_data = {}
            if num_rows > 1:
                for key, value in by_column.items():
                    row_data[key] = value[row_num]
            else:
                row_data = by_column
            # filter empty rows.
            is_empty = True
            for value in row_data.values():
                if value and len(value.strip()) > 0:
                    is_empty = False
                    break
            if not is_empty:
                row_data['rowId'] = str(row_num)
                rows.append(row_data)

        return rows

    def _set_activity_from_previous(self):
        """
        Sets Running Sheet Species stock total from previous Licence Running Sheet.
        :return:
        """
        previous_licence = self._return.application.previous_application.licence
        if previous_licence:
            # TODO : for the reissue of licences. Species stock count must carry over. Nb. change in species.
            '''      
            table = {'data': None}              
            for each species in previous_licence
                try:
                    return_table = self._return.returntable_set.get(name=_resource_name)
                    rows = [_return_row.data for _return_row in _return_table.returnrow_set.all()]
                    table['data'] = rows
                    table['echo'] = 1
                    table['totalRecords'] = str(rows.__len__())
                    table['totalDisplayRecords'] = str(rows.__len__())
                except ReturnTable.DoesNotExist:
                    self._table = self._NO_ACTIVITY
                self._create_return_data(self._return, _species_id, _table)
            '''

    def _get_licence_return(self, licence_no):
        """
        Method to retrieve Return with Running Sheet from a Licence No.
        :param licence_no:
        :return: a Return object.
        """
        try:
            return Return.objects.filter(licence__licence_number=licence_no,
                                         return_type__data_format=ReturnType.FORMAT_SHEET
                                         ).first()
        except Return.DoesNotExist:
            raise ValidationError({'error': 'Error exception.'})

    def _add_transfer_activity(self, request):
        """
        Add transfer activity to a validated receiving licence return.
        :param request:
        :return:
        """
        if not request.data.get('transfer'):
            return False
        _data = request.data.get('transfer').encode('utf-8')
        _transfers = ast.literal_eval(_data)
        if isinstance(_transfers, tuple):
            for transfer in _transfers:
                a_transfer = ReturnActivity.factory(transfer)
                a_transfer.store_transfer_activity(transfer['species_id'], request, self._return)
        else:
            a_transfer = ReturnActivity.factory(_transfers)
            a_transfer.store_transfer_activity(_transfers['species_id'], request, self._return)

    def _is_valid_transfer_licence(self, _licence):
        """
        Method to check if licence is current.
        :return: boolean
        """
        return True if self._get_licence_return(_licence) else False

    def _is_valid_transfer_quantity(self, request):
        """
        Method to check transfer transfer quantity does not exceed total.
        :param request:
        :return: boolean
        """
        if not request.data.get('transfer'):
            return False
        data = request.data.get('transfer').encode('utf-8')
        transfers = ast.literal_eval(data)
        quantity = transfers['qty']
        species_id = transfers['transfer']
        '''
        return_table = ReturnTable.objects.get(
            name=species, ret=to_return)[0]
        rows = ReturnRow.objects.filter(return_table=return_table)  # optimistic load of rows.
        table_rows = []
        row_exists = False
        total = 0
        for row in rows:  # update total and status for accepted activity.
            if row.data[self._ACTIVITY_DATE] == self.date:
                row_exists = True
                row.data[self._TRANSFER] = ReturnActivity._TRANSFER_STATUS_ACCEPT
                row.data[self._TOTAL] = int(row.data[self._TOTAL]) - int(self.qty)
                table_rows.append(row.data)
                break
        for row in rows:  # update totals for subsequent activities.
            if row_exists and int(row.data[self._ACTIVITY_DATE]) > int(self.date):
                row.data[self._TOTAL] = int(row.data[self._TOTAL]) - int(self.qty)
            table_rows.append(row.data)
        '''

    def __str__(self):
        return self._return.lodgement_number


class ReturnActivity(object):
    """
    An Activity relating to the Transfer of Stock.
    """

    _TRANSFER_STATUS_NONE = ''
    _TRANSFER_STATUS_NOTIFY = 'Notified'
    _TRANSFER_STATUS_ACCEPT = 'Accepted'
    _TRANSFER_STATUS_DECLINE = 'Declined'

    # Activity properties.
    _ACTIVITY_DATE = 'date'
    _COMMENT = 'comment'
    _TRANSFER = 'transfer'
    _QUANTITY = 'qty'
    _LICENCE = 'licence'
    _ACTIVITY = 'activity'
    _TOTAL = 'total'
    _ROWID = 'rowId'

    def __init__(self, transfer):
        self.date = transfer[self._ACTIVITY_DATE]
        self.comment = transfer[self._COMMENT]
        self.transfer = transfer[self._TRANSFER]
        self.qty = transfer[self._QUANTITY]
        self.licence = transfer[self._LICENCE]
        self.total = ''
        self.rowId = '0'
        self.activity = transfer[self._ACTIVITY]

    def get_licence_return(self):
        """
        Method to retrieve Return with Running Sheet from a Licence No.
        :return: a Return object.
        """
        try:
            return Return.objects.filter(licence__licence_number=self.licence,
                                         return_type__data_format=ReturnType.FORMAT_SHEET
                                         ).first()
        except Return.DoesNotExist:
            raise ValidationError({'error': 'Error exception.'})

    @staticmethod
    def factory(transfer):
        if transfer[ReturnActivity._TRANSFER] == ReturnActivity._TRANSFER_STATUS_NOTIFY:
            return NotifyTransfer(transfer)
        if transfer[ReturnActivity._TRANSFER] == ReturnActivity._TRANSFER_STATUS_ACCEPT:
            return AcceptTransfer(transfer)
        if transfer[ReturnActivity._TRANSFER] == ReturnActivity._TRANSFER_STATUS_DECLINE:
            return DeclineTransfer(transfer)

        return None


class NotifyTransfer(ReturnActivity):
    """
    Notification of a Transfer Activity.
    """

    def __init__(self, transfer):
        super(NotifyTransfer, self).__init__(transfer)
        self.activity = ReturnSheet._ACTIVITY_TYPES[transfer[self._ACTIVITY]]['outward']

    @transaction.atomic
    def store_transfer_activity(self, species, request, from_return):
        """
        Saves the Transfer Activity under the Receiving Licence return for species.
        :return: _new_transfer boolean.
        """
        to_return = self.get_licence_return()
        self.licence = from_return.licence.licence_number

        try:
            return_table = ReturnTable.objects.get_or_create(
                name=species, ret=to_return)[0]
            rows = ReturnRow.objects.filter(return_table=return_table)  # TODO: optimistic locking of rows.
            table_rows = []
            row_exists = False
            total = 0
            row_cnt = 0
            self.rowId = str(row_cnt)
            for row in rows:
                if row.data[self._ACTIVITY_DATE] == self.date:  # update to record
                    row_exists = True
                    row.data[self._QUANTITY] = self.qty
                    row.data[self._COMMENT] = self.comment
                    row.data[self._TRANSFER] = self.transfer
                total = row.data[self._TOTAL]
                table_rows.append(row.data)
                row_cnt = row_cnt + 1
                self.rowId = str(row_cnt)
            if not row_exists:
                self.total = total
                table_rows.append(self.__dict__)
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in table_rows]
            ReturnRow.objects.bulk_create(return_rows)
            # log transaction
            from_return.log_user_action(ReturnUserAction.ACTION_SUBMIT_TRANSFER.format(from_return), request)

            if not row_exists:
                send_sheet_transfer_email_notification(request, to_return, from_return)

            return row_exists
        except BaseException:
            raise


class AcceptTransfer(ReturnActivity):
    """
    A ReturnActivity that is an Accepted Transfer.
    """

    def __init__(self, transfer):
        super(AcceptTransfer, self).__init__(transfer)

    @transaction.atomic
    def store_transfer_activity(self, species, request, from_return):
        """
        Saves the Transfer Activity under the Receiving Licence return for species.
        :return: _new_transfer boolean.
        """
        to_return = self.get_licence_return()

        try:
            return_table = ReturnTable.objects.get(
                name=species, ret=to_return)
            rows = ReturnRow.objects.filter(return_table=return_table)  # TODO: Requires optimistic locking of rows.
            table_rows = []
            row_exists = False
            for row in rows:  # update total and status for accepted activity.
                if row.data[self._ACTIVITY_DATE] == self.date:
                    row_exists = True
                    row.data[self._TRANSFER] = ReturnActivity._TRANSFER_STATUS_ACCEPT
                    row.data[self._TOTAL] = int(row.data[self._TOTAL]) - int(self.qty)
                    break
            for row in rows:  # update totals for subsequent activities.
                if row_exists and int(row.data[self._ACTIVITY_DATE]) > int(self.date):
                    row.data[self._TOTAL] = int(row.data[self._TOTAL]) - int(self.qty)
                table_rows.append(row.data)
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in table_rows]
            ReturnRow.objects.bulk_create(return_rows)
            # log transaction
            from_return.log_user_action(ReturnUserAction.ACTION_ACCEPT_TRANSFER.format(from_return), request)

            return row_exists
        except BaseException:
            raise


class DeclineTransfer(ReturnActivity):
    """
    A ReturnActivity that is an Declined Transfer.
    """

    def __init__(self, transfer):
        super(DeclineTransfer, self).__init__(transfer)

    @transaction.atomic
    def store_transfer_activity(self, species, request, from_return):
        """
        Saves the Transfer Activity under the Receiving Licence return for species.
        :return: _new_transfer boolean.
        """
        to_return = self.get_licence_return()

        try:
            return_table = ReturnTable.objects.get(
                name=species, ret=to_return)
            rows = ReturnRow.objects.filter(return_table=return_table)  # TODO: requires optimistic locking of rows.
            table_rows = []
            row_exists = False
            for row in rows:  # update status for selected activity.
                if row.data[self._ACTIVITY_DATE] == self.date:
                    row_exists = True
                    row.data[self._TRANSFER] = ReturnActivity._TRANSFER_STATUS_DECLINE
                table_rows.append(row.data)

            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in table_rows]
            ReturnRow.objects.bulk_create(return_rows)
            # log transaction
            from_return.log_user_action(ReturnUserAction.ACTION_DECLINE_TRANSFER.format(from_return), request)

            return row_exists
        except BaseException:
            raise


class ReturnTable(RevisionedMixin):
    ret = models.ForeignKey(Return)

    name = models.CharField(max_length=50)

    class Meta:
        app_label = 'wildlifecompliance'


class ReturnRow(RevisionedMixin):
    return_table = models.ForeignKey(ReturnTable)

    data = JSONField(blank=True, null=True)

    class Meta:
        app_label = 'wildlifecompliance'


class ReturnUserAction(UserAction):
    ACTION_CREATE = "Lodge Return {}"
    ACTION_SUBMIT_REQUEST = "Submit Return {}"
    ACTION_ACCEPT_REQUEST = "Accept Return {}"
    ACTION_SAVE_REQUEST = "Save Return {}"
    ACTION_SUBMIT_TRANSFER = "Request for transfer of species stock from Return {}"
    ACTION_ACCEPT_TRANSFER = "Accepted the transfer of species stock to Return {}"
    ACTION_DECLINE_TRANSFER = "Declined the transfer of species stock to Return {}"
    ACTION_ASSIGN_TO = "Assign to {}"
    ACTION_UNASSIGN = "Unassign"
    ACTION_DECLINE_REQUEST = "Decline request"
    ACTION_ID_REQUEST_AMENDMENTS = "Request amendments"
    ACTION_REMINDER_SENT = "Reminder sent for return {}"
    ACTION_STATUS_CHANGE = "Change status to Due for return {}"

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, return_obj, action, user):
        return cls.objects.create(
            return_obj=return_obj,
            who=user,
            what=str(action)
        )

    return_obj = models.ForeignKey(Return, related_name='action_logs')


class ReturnLogEntry(CommunicationsLogEntry):
    return_obj = models.ForeignKey(Return, related_name='comms_logs')

    class Meta:
        app_label = 'wildlifecompliance'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.return_obj.id
        super(ReturnLogEntry, self).save(**kwargs)


class ReturnInvoice(models.Model):
    invoice_return = models.ForeignKey(Return, related_name='invoices')
    invoice_reference = models.CharField(
        max_length=50, null=True, blank=True, default='')

    class Meta:
        app_label = 'wildlifecompliance'

    def __str__(self):
        return 'Return {} : Invoice #{}'.format(
            self.invoice_return.id, self.invoice_reference)

    # Properties
    # ==================
    @property
    def active(self):
        try:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
            return False if invoice.voided else True
        except Invoice.DoesNotExist:
            pass
        return False
