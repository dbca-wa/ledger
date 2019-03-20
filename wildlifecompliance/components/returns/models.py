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

    _SHEET_SCHEMA = {"name": "sheet", "title": "Running Sheet of Return Data", "resources": [{"name":
                     "SpecieID", "path": "", "title": "Return Data for Specie", "schema": {"fields": [{"name":
                     "date", "type": "date", "format": "fmt:%d/%m/%Y", "constraints": {"required": True}}, {"name":
                     "activity", "type": "string", "constraints": {"required": True}}, {"name": "qty", "type":
                     "number", "constraints": {"required": True}}, {"name": "total", "type": "number",
                     "constraints": {"required": True}}, {"name": "licence", "type": "string"}, {"name": "comment",
                     "type": "string"}]}}]}

    _NO_ACTIVITY = {"echo": 1, "totalRecords": "0", "totalDisplayRecords": "0", "data": []}

    _ACTIVITY_TYPES = {"SA01": "Stock", "SA02": "In through Import", "SA03": "In through birth",
                       "SA04": "In through transfer", "SA05": "Out through export", "SA06": "Out through death",
                       "SA07": "Out through transfer other", "SA08": "Out through transfer dealer", '': None}

    _MOCK_TABLE = {'name': 'SPEC01', 'data': [{'rowId': '0', 'date': '2019/01/23', 'activity': 'SA01', 'qty': '5', 'total': '5',
                  'comment': 'Initial Stock Taking', 'licence': ''}, {'rowId': '1', 'date': '2019/01/31', 'activity': 'SA03',
                  'qty': '3', 'total': '8', 'comment': 'Birth of three new species', 'licence': ''}]}

    _MOCK_SPECIES = ['SPEC01', 'SPEC02', 'SPEC03']

    def __init__(self, a_return):
        self._return = a_return
        self._return.return_type.data_descriptor = self._SHEET_SCHEMA
        self._species_list = []
        for _species in ReturnTable.objects.filter(ret=a_return):
            self._species_list.append(_species.name)
        self._table = {'data': None}

    def _get_table_rows(self, _data):
        """
        Gets the formatted row of data from Species data
        :param _data:
        :return: by_column is of format {'col_header':[row1_val, row2_val,...],...}
        """
        by_column = dict([])
        for key in _data[0].keys():
            key_values = []
            for cnt in range(_data.__len__()):
                key_values.append(_data[cnt][key])
            by_column[key] = key_values
        num_rows = len(list(by_column.values())[0]) if len(by_column.values()) > 0 else 0
        self._rows = []
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
                self._rows.append(row_data)

    def _create_return_data(self, ret, tables_info, _data):
        """
        Saves row of data to db.
        :param ret:
        :param tables_info:
        :param _data:
        :return:
        """
        self._get_table_rows(tables_info, _data)
        if self._rows:
            return_table = ReturnTable.objects.get_or_create(
                name=tables_info, ret=ret)[0]
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in self._rows]
            ReturnRow.objects.bulk_create(return_rows)

    @property
    def data(self):
        return self.table['data']

    @property
    def table(self):
        """
        Running Sheet data for Species.
        :return: formatted data.
        """
        return self.get_table('NONE') if not self._species_list else self._species_list[0]

    def get_table(self, _species_id):
        """
        Gets a return Running Sheet Species data for table format.
        :return: formatted data {'name': 'speciesId', 'data': [{'date': '2019/01/23', 'activity': 'SA01', ..., }]}
        """
        _row = {}
        _result = []
        for resource in self._return.return_type.resources:
            _resource_name = _species_id
            _schema = Schema(resource.get('schema'))
            try:
                _return_table = self._return.returntable_set.get(name=_resource_name)
                rows = [_return_row.data for _return_row in _return_table.returnrow_set.all()]
                _validated_rows = _schema.rows_validator(rows)
                self._table['data'] = rows
            except ReturnTable.DoesNotExist:
                self._table = self._NO_ACTIVITY
        #self._table = self._MOCK_TABLE

        return self._table

    def set_table(self, _species_name, _data):
        """
        Sets data for Species Running Sheet information.
        :param _species_name:
        :param _data:
        :return:
        """
        self._create_return_data(self._return, _species_name, _data)

    def get_activity_list(self):
        """
        Method to return the full list of activity types available for all Species.
        :return: List of Activity Types.
        """
        return self._ACTIVITY_TYPES

    def get_species_list(self):

        _species = self._species_list

       # _species = self._MOCK_SPECIES

        return _species

    def is_valid(self):
        pass

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
