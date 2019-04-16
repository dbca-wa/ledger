import re
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import transaction
from preserialize.serialize import serialize
from ledger.accounts.models import EmailUser, Document
from wildlifecompliance.components.applications.models import ApplicationDocument
from wildlifecompliance.components.applications.serializers import SaveApplicationSerializer
import json
from wildlifecompliance.components.licences.models import LicencePurpose, DefaultPurpose, LicenceActivity, DefaultActivity
from wildlifecompliance.utils.assess_utils import pdflatex, get_activity_sys_answers
import traceback


class SchemaParser(object):

    def create_data_from_form(
            self,
            schema,
            post_data,
            file_data,
            comment_data=False):
        data = {}
        comment_data_list = {}
        if comment_data:
            comment_fields_search = CommentDataSearch()
        try:
            for item in schema:
                data.update(
                    self._create_data_from_item(
                        item,
                        post_data,
                        file_data,
                        0,
                        '',
                        activity_name=item['name']))
                if comment_data:
                    comment_fields_search.extract_special_fields(
                        item, post_data, file_data, 0, '')
            if comment_data:
                comment_data_list = comment_fields_search.comment_data
        except BaseException:
            traceback.print_exc()
        if comment_data:
            return [data], comment_data_list

        return [data]

    def _create_data_from_item(self, item, post_data, file_data, repetition, suffix, **kwargs):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            if item['type'] in ['checkbox' 'declaration']:
                item_data[item['name']] = extended_item_name in post_data
            elif item['type'] == 'file':
                if extended_item_name in file_data:
                    item_data[item['name']] = str(
                        file_data.get(extended_item_name))
                    # TODO save the file here
                elif extended_item_name + '-existing' in post_data and len(post_data[extended_item_name + '-existing']) > 0:
                    item_data[item['name']] = post_data.get(
                        extended_item_name + '-existing')
                else:
                    item_data[item['name']] = ''
            else:
                if extended_item_name in post_data:
                    if item['type'] == 'multi-select':
                        item_data[item['name']] = post_data.getlist(
                            extended_item_name)
                    else:
                        item_data[item['name']] = post_data.get(extended_item_name)
        else:
            if 'repetition' in item:
                item_data = self.generate_item_data(extended_item_name,
                                            item,
                                            item_data,
                                            post_data,
                                            file_data,
                                            len(post_data[item['name']]),
                                            suffix,
                                            **kwargs)
            else:
                item_data = self.generate_item_data(
                    extended_item_name,
                    item,
                    item_data,
                    post_data,
                    file_data,
                    1,
                    suffix,
                    **kwargs)

        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    # print(child)
                    item_data.update(
                        self._create_data_from_item(
                            child,
                            post_data,
                            file_data,
                            repetition,
                            suffix,
                            **kwargs))

        return item_data

    def generate_item_data(
            self,
            item_name,
            item,
            item_data,
            post_data,
            file_data,
            repetition,
            suffix, **kwargs):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                # print(child_item)
                child_data.update(self._create_data_from_item(
                    child_item, post_data, file_data, 0, '{}-{}'.format(suffix, rep),
                    **kwargs))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data


def _extend_item_name(name, suffix, repetition):
    return '{}{}-{}'.format(name, suffix, repetition)


class CommentDataSearch(object):

    def __init__(self):
        self.comment_data = {}

    def extract_comment_data(self, item, post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item, k):
                values.append({k: post_data[k]})
        if values:
            for v in values:
                for k, v in v.items():
                    parts = k.split('{}'.format(item))
                    if len(parts) > 1:
                        ref_parts = parts[1].split('-comment-field')
                        if len(ref_parts) > 1:
                            res = {'{}'.format(item): v}
        return res

    def extract_special_fields(
            self,
            item,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            self.comment_data.update(
                self.extract_comment_data(
                    extended_item_name, post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, len(post_data[item['name']]), suffix)
            else:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, 1, suffix)

        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    item_data.update(
                        self.extract_special_fields(
                            child,
                            post_data,
                            file_data,
                            repetition,
                            suffix))

        return item_data

    def generate_item_data_special_field(
            self,
            item_name,
            item,
            item_data,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(
                    child_item, post_data, file_data, 0, '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data


class SpecialFieldsSearch(object):

    def __init__(self, lookable_fields):
        self.lookable_fields = lookable_fields
        self.special_fields = {}

    def extract_special_fields(
            self,
            item,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            for f in self.lookable_fields:
                if item['type'] in ['checkbox' 'declaration']:
                    val = None
                    val = item.get(f, None)
                    if val:
                        item_data[f] = extended_item_name in post_data
                        self.special_fields.update(item_data)
                else:
                    if extended_item_name in post_data:
                        val = None
                        val = item.get(f, None)
                        if val:
                            if item['type'] == 'multi-select':
                                item_data[f] = ','.join(
                                    post_data.getlist(extended_item_name))
                            else:
                                item_data[f] = post_data.get(
                                    extended_item_name)
                            self.special_fields.update(item_data)
        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, len(post_data[item['name']]), suffix)
            else:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, 1, suffix)

        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    item_data.update(
                        self.extract_special_fields(
                            child,
                            post_data,
                            file_data,
                            repetition,
                            suffix))

        return item_data

    def generate_item_data_special_field(
            self,
            item_name,
            item,
            item_data,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(
                    child_item, post_data, file_data, 0, '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data

def update_schema_name(item_data, id):

    for item in item_data:
        # print('name')
        item['name'] = item['name'] + '_' + str(id)
        # print(item['name'])
        if 'children' in item:
            update_schema_name(item['children'], id)
            # print(item['children'])
