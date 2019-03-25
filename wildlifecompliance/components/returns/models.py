from __future__ import unicode_literals
from django.db import models, transaction
from django.contrib.postgres.fields.jsonb import JSONField
from django.utils import timezone
from ledger.accounts.models import EmailUser, RevisionedMixin
from wildlifecompliance.components.returns.utils_schema import Schema
from wildlifecompliance.components.applications.models import ApplicationCondition, Application
from wildlifecompliance.components.main.models import CommunicationsLogEntry, UserAction
from wildlifecompliance.components.returns.email import send_external_submit_email_notification, \
                                                        send_return_accept_email_notification


class ReturnType(models.Model):
    """
    A Type to identify the method used to facilitate Return.
    """
    RETURN_TYPE_CHOICES = (('sheet', 'Sheet'),
                           ('question', 'Question'),
                           ('data', 'Data'))

    Name = models.TextField(null=True, blank=True, max_length=200)
    data_descriptor = JSONField()
    return_type = models.CharField(
        'Type',
        max_length=30,
        choices=RETURN_TYPE_CHOICES,
        default=RETURN_TYPE_CHOICES[0][0])

    class Meta:
        app_label = 'wildlifecompliance'

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


class Return(models.Model):
    """
    A number of requirements relating to a Licence condition.
    """
    PROCESSING_STATUS_CHOICES = (('due', 'Due'),
                                 ('overdue', 'Overdue'),
                                 ('draft', 'Draft'),
                                 ('future', 'Future'),
                                 ('with_curator', 'With Curator'),
                                 ('accepted', 'Accepted'),
                                 )
    CUSTOMER_STATUS_CHOICES = (('due', 'Due'),
                               ('overdue', 'Overdue'),
                               ('draft', 'Draft'),
                               ('future', 'Future'),
                               ('under_review', 'Under Review'),
                               ('accepted', 'Accepted'),

                               )
    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    application = models.ForeignKey(Application, related_name='returns')
    licence = models.ForeignKey(
        'wildlifecompliance.WildlifeLicence',
        related_name='returns')
    due_date = models.DateField()
    text = models.TextField(blank=True)
    processing_status = models.CharField(
        choices=PROCESSING_STATUS_CHOICES, max_length=20)
    customer_status = models.CharField(
        choices=CUSTOMER_STATUS_CHOICES,
        max_length=20,
        default=CUSTOMER_STATUS_CHOICES[1][0])
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
    def type(self):
        return self.return_type.Name

    @property
    def table(self):
        tables = []
        for resource in self.return_type.resources:
            resource_name = resource.get('name')
            schema = Schema(resource.get('schema'))
            headers = []
            for f in schema.fields:
                header = {
                    "title": f.name,
                    "required": f.required,
                    "type": f.type.name
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
                return_table = self.returntable_set.get(name=resource_name)
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

    @property
    def sheet(self):
        """
        A Running sheet of Return data.
        :return: ReturnSheet with activity data for species.
        """
        return ReturnSheet(self) if self.has_sheet else None

    @property
    def has_question(self):
        """
        Property defining if the Return is Question based.
        :return: Boolean
        """
        return True if self.return_type.Name == 'question' else False

    @property
    def has_data(self):
        """
        Property defining if the Return is Data based.
        :return: Boolean
        """
        return True if self.return_type.Name == 'data' else False

    @property
    def has_sheet(self):
        """
        Property defining if the Return is Running Sheet based.
        :return: Boolean
        """
        return True if self.return_type.Name == 'sheet' else False

    def log_user_action(self, action, request):
        return ReturnUserAction.log_action(self, action, request.user)

    def set_submitted(self, request):
        with transaction.atomic():
            try:
                if self.processing_status == 'future' or 'due':
                    self.customer_status = "under_review"
                    self.processing_status = "with_curator"
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
            self.processing_status = 'accepted'
            self.customer_status = 'accepted'
            self.save()
            self.log_user_action(
                ReturnUserAction.ACTION_ACCEPT_REQUEST.format(
                    self.id), request)
            send_return_accept_email_notification(self, request)


class ReturnData(object):
    """
    Informational data of requirements supporting licence condition.
    """
    def __init__(self, a_return):
        self._return = a_return

    def __str__(self):
        return 'Return-Data-{0}'.format(self._return.id)


class ReturnQuestion(object):
    """
    Informational question of requirements supporting licence condition.
    """
    def __init__(self, a_return):
        self._return = a_return

    def __str__(self):
        return 'Return-Question-{0}'.format(self._return.id)


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
                    "": {"label": "", "auto": "false", "licence": "false", "pay": "false"}
                      }

    _MOCK_LICENCE_SPECIES = ['S000001', 'S000002', 'S000003', 'S000004']

    def __init__(self, a_return):
        self._return = a_return
        self._return.return_type.data_descriptor = self._SHEET_SCHEMA
        self._species_list = []
        self._licence_species_list = []
        self._table = {'data': None}
        # build list of currently added Species.
        self._species = self._DEFAULT_SPECIES
        for _species in ReturnTable.objects.filter(ret=a_return):
            self._species_list.append(_species.name)
            self._species = _species.name
        # build list of Species available on Licence.
        self._licence_species_list = self._MOCK_LICENCE_SPECIES

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
            for key, value in by_column.items():
                row_data[key] = value[row_num]
            # filter empty rows.
            is_empty = True
            for value in row_data.values():
                if len(value[row_num].strip()) > 0:
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
    def licence_species_list(self):
        """
        List of Species applicable for Running Sheet Return Licence.
        :return: List of Species.
        """
        return self._licence_species_list

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

    def set_activity(self, _species_id, _data):
        """
        Sets Running Sheet Activity for the movement of Species stock.
        :param _species_id:
        :param _data:
        :return:
        """
        self._create_return_data(self._return, _species_id, _data)
        self.set_species(_species_id)

    def set_species(self, _species):
        """
        Sets the species for the current Running Sheet.
        :param _species:
        :return:
        """
        self._species = _species
        self._species_list.add(_species)

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

    def __str__(self):
        return 'Return-Sheet-{0}'.format(self._return.id)


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
