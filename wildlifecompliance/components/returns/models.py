from __future__ import unicode_literals
from django.db import models, transaction
from django.db.models.signals import post_save
from django.contrib.postgres.fields.jsonb import JSONField
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import FieldError
from ledger.accounts.models import EmailUser, RevisionedMixin
from wildlifecompliance.components.returns.utils_schema import Schema
from wildlifecompliance.components.applications.models import ApplicationCondition, Application
from wildlifecompliance.components.main.models import CommunicationsLogEntry, UserAction
from wildlifecompliance.components.returns.email import send_external_submit_email_notification, \
                                                        send_return_accept_email_notification

import json, ast


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
    RETURN_TYPE_SHEET = 'sheet'
    RETURN_TYPE_QUESTION = 'question'
    RETURN_TYPE_DATA = 'data'
    RETURN_TYPE_CHOICES = (
        (RETURN_TYPE_SHEET, 'Sheet'),
        (RETURN_TYPE_QUESTION, 'Question'),
        (RETURN_TYPE_DATA, 'Data')
    )
    name = models.CharField(null=True, blank=True, max_length=100)
    description = models.TextField(null=True, blank=True, max_length=256)
    data_descriptor = JSONField()
    data_format = models.CharField(
        'Data format',
        max_length=30,
        choices=RETURN_TYPE_CHOICES,
        default=RETURN_TYPE_SHEET)
    data_template = models.FileField(upload_to=template_directory_path, null=True, blank=True)
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
    application = models.ForeignKey(Application, related_name='returns')
    licence = models.ForeignKey(
        'wildlifecompliance.WildlifeLicence',
        related_name='returns')
    due_date = models.DateField()
    text = models.TextField(blank=True)
    processing_status = models.CharField(
        choices=PROCESSING_STATUS_CHOICES,
        max_length=20,
        default=RETURN_PROCESSING_STATUS_FUTURE)
    assigned_to = models.ForeignKey(
        EmailUser,
        related_name='wildlifecompliance_return_assignments',
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
        related_name='disturbance_compliances')
    reminder_sent = models.BooleanField(default=False)
    post_reminder_sent = models.BooleanField(default=False)
    return_type = models.ForeignKey(ReturnType, null=True)
    nil_return = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)

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
    def regions(self):
        return self.application.regions_list

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
        table = []
        if self.has_sheet:
            return self.sheet.table
        if self.has_data:
            return self.data.table
        if self.has_question:
            return self.question.table
        return table

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
        return True if self.format == ReturnType.RETURN_TYPE_QUESTION else False

    @property
    def has_data(self):
        """
        Property defining if the Return is Data based.
        :return: Boolean
        """
        return True if self.format == ReturnType.RETURN_TYPE_DATA else False

    @property
    def has_sheet(self):
        """
        Property defining if the Return is Running Sheet based.
        :return: Boolean
        """
        return True if self.format == ReturnType.RETURN_TYPE_SHEET else False

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

    def set_submitted(self, request):
        with transaction.atomic():
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
                self.log_user_action(
                    ReturnUserAction.ACTION_SUBMIT_REQUEST.format(
                        self.id), request)
                send_external_submit_email_notification(request, self)
                # send_submit_email_notification(request,self)
            except BaseException:
                raise

    def accept(self, request):
        with transaction.atomic():
            self.processing_status = Return.RETURN_PROCESSING_STATUS_ACCEPTED
            self.save()
            self.log_user_action(
                ReturnUserAction.ACTION_ACCEPT_REQUEST.format(
                    self.id), request)
            send_return_accept_email_notification(self, request)

    def store(self, request):
        """
        Save the current state of the Return.
        :param request:
        :return:
        """
        pass

    def submit(self, request):
        """
        Submit Return to Curator.
        :param request:
        :return:
        """
        pass

    def amend(self, request):
        """
        Request amendment for Return.
        :param request:
        :return:
        """
        pass

    def discard(self, request):
        """
        Discard a Return.
        :param request:
        :return:
        """
        pass

    def create_return_data(self, table_name, table_rows):
        if table_rows:
            return_table = ReturnTable.objects.get_or_create(
                name=table_name, ret=self._return)[0]
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in table_rows]
            ReturnRow.objects.bulk_create(return_rows)

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
                    "type": f.type.name
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
                    self._create_return_data_from_post_data(returns_tables.encode('utf-8'), request.data)
                else:
                    raise FieldError('Enter data in correct format.')

    def _is_post_data_valid(self, tables_info, post_data):
        """
        Validates table data against the schema,
        :param tables_info:
        :param post_data:
        :return:
        """
        table_rows = self._get_table_rows_from_post(tables_info, post_data)
        if len(table_rows) == 0:
            return False
        schema = Schema(self._return.return_type.get_schema_by_name(tables_info))
        if not schema.is_all_valid(table_rows):
            return False
        return True

    def _get_table_rows_from_post(self, table_name, post_data):
        """
        Build row of data.
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

    def build_table(self, rows):
        """
        Method to create and validate rows of data to the table schema without persisting.
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

    def _create_return_data(self, table_name, table_rows):
        """
        Method to persist Return record.
        :return:
        """
        self._return.create_return_data(table_name, table_rows)

        return True

    def _create_return_data_from_post_data(self, tables_info, post_data):
        """
        Writes to db.
        :param tables_info:
        :param post_data:
        :return:
        """
        rows = self._get_table_rows_from_post(tables_info, post_data)
        if rows:
            return_table = ReturnTable.objects.get_or_create(
                name=tables_info, ret=self._return)[0]
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in rows]
            ReturnRow.objects.bulk_create(return_rows)

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
            resource_name = ReturnType.RETURN_TYPE_QUESTION
            schema = Schema(resource.get('schema'))
            headers = []
            for f in schema.fields:
                header = {
                    "label": f.data['label'],
                    "name": f.data['name'],
                    "required": f.required,
                    "type": f.type.name,
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
        self._create_return_data(self._return, request.POST)

    def _get_table_rows(self, _data):
        """
        Gets the formatted row of data from Species data
        :param _data:
        :return: by_column is of format {'col_header':[row1_val, row2_val,...],...}
        """
        by_column = dict([])
        for key in _data.keys():
            by_column[key] = _data[key]
        self._rows = []
        self._rows.append(by_column)

    def _create_return_data(self, ret, _data):
        """
        Saves row of data to db.
        :param ret:
        :param _data:
        :return:
        """
        self._get_table_rows(_data)
        if self._rows:
            return_table = ReturnTable.objects.get_or_create(
                name=ReturnType.RETURN_TYPE_QUESTION, ret=ret)[0]
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in self._rows]
            ReturnRow.objects.bulk_create(return_rows)

    def __str__(self):
        return self._return.lodgement_number


class ReturnSheet(object):
    """
    Informational Running Sheet of Species requirements supporting licence condition.
    """
    _DEFAULT_SPECIES = '0000000'

    _SHEET_SCHEMA = {"name": "sheet", "title": "Running Sheet of Return Data", "resources": [{"name":
                     "SpecieID", "path": "", "title": "Return Data for Specie", "schema": {"fields": [{"name":
                     "date", "type": "date", "format": "fmt:%d/%m/%Y", "constraints": {"required": True}}, {"name":
                     "activity", "type": "string", "constraints": {"required": True}}, {"name": "qty", "type":
                     "number", "constraints": {"required": True}}, {"name": "total", "type": "number",
                     "constraints": {"required": True}}, {"name": "licence", "type": "string"}, {"name": "comment",
                     "type": "string"}, {"name": "transfer", "type": "boolean"}]}}]}

    _NO_ACTIVITY = {"echo": 1, "totalRecords": "0", "totalDisplayRecords": "0", "data": []}

    _ACTIVITY_TYPES = {
        "SA01": {"label": "Stock", "auto": "false", "licence": "false", "pay": "false"},
        "SA02": {"label": "In through import", "auto": "false", "licence": "false", "pay": "false"},
        "SA03": {"label": "In through birth", "auto": "false", "licence": "false", "pay": "false"},
        "SA04": {"label": "In through transfer", "auto": "true", "licence": "false", "pay": "false"},
        "SA05": {"label": "Out through export", "auto": "false", "licence": "false", "pay": "false"},
        "SA06": {"label": "Out through death", "auto": "false", "licence": "false", "pay": "false"},
        "SA07": {"label": "Out through transfer other", "auto": "false", "licence": "true", "pay": "true"},
        "SA08": {"label": "Out through transfer dealer", "auto": "false", "licence": "true", "pay": "false"},
        "": {"label": "", "auto": "false", "licence": "false", "pay": "false"}}

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

    def _get_table_rows(self, _data):
        """
        Gets the formatted row of data from Species data
        :param _data:
        :return: by_column is of format {'col_header':[row1_val, row2_val,...],...}
        """
        by_column = dict([])
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

        self._rows = []
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
                self._rows.append(row_data)

    def _create_return_data(self, ret, _species_id, _data):
        """
        Saves row of data to db.
        :param ret:
        :param _species_id:
        :param _data:
        :return:
        """
        self._get_table_rows(_data)
        if self._rows:
            return_table = ReturnTable.objects.get_or_create(
                name=_species_id, ret=ret)[0]
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in self._rows]
            ReturnRow.objects.bulk_create(return_rows)

    @property
    def table(self):
        """
        Running Sheet Table of data for Species. Defaults to a Species on the Return if exists.
        :return: formatted data.
        """
        return self.get_activity(self._species)['data']

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
        :return: List of Activities applicable for Running Sheet.
        """
        return self._ACTIVITY_TYPES

    def get_activity(self, _species_id):
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

    def set_activity(self, _species, _data):
        """
        Sets Running Sheet Activity for the movement of Species stock.
        :param _species:
        :param _data:
        :return:
        """
        self._create_return_data(self._return, _species, _data)
        self.set_species(_species)

    def set_activity_from_previous(self):
        """
        Sets Running Sheet Activity for the movement of Species stock from previous Licence Running Sheet.
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

    @staticmethod
    def set_licence_species(self):
        """
        Sets the species from the licence for the current Running Sheet.
        :return:
        """
        _data = []
        # TODO: create default entries for each species on the licence.
        # for _species in self._return.licence:
        #    self.set_activity(_species, _data)
        pass

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

    def is_valid_licence(self, _licence_no):
        """
        Method to check if licence is current.
        :param _licence_no:
        :return: boolean
        """
        return False

    def send_transfer_notification(self, _license_no):
        """
        send email notification for transfer of stock to receiving license holder.
        :param _license_no:
        :return: boolean
        """
        return False

    def get_licensee_contact(self, _license_no):
        """
        Gets a valid License holder contact details.
        :param _license_no:
        :return:
        """
        return None

    def store(self, request):
        """
        Save the current state of this Return Sheet.
        :param request:
        :return:
        """
        for species in self.species_list:
            try:
                _data = request.data.get(species).encode('utf-8')
                _data = tuple(ast.literal_eval(_data))
                self.set_activity(species, _data)
            except AttributeError:
                continue

    def __str__(self):
        return self._return.lodgement_number


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
