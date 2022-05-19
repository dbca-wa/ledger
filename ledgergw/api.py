from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ledger.accounts import models
from django.contrib.auth.models import Group
from ledgergw import models as ledgergw_models
from ledgergw import reports
from ledger.api import models as ledgerapi_models
from ledger.api import utils as ledgerapi_utils
#from ledgergw import common
from django.db.models import Q
from ledger.checkout import utils
from ledger.payments import utils as payments_utils
from ledger.payments.invoice import utils as utils_ledger_payment_invoice
from oscar.apps.order.models import Order
from ledger.payments.invoice.models import Invoice
from ledger.payments import models as payment_models
from ledger.payments.bpoint import models as payment_bpoint_models
from ledger.basket import models as basket_models
from ledger.order import models as order_models
from django.core.files.base import ContentFile
from django.utils.crypto import get_random_string
from ledger.payments.models import Invoice, BpointToken
from rest_framework.response import Response
from rest_framework import viewsets, serializers, status, generics, views
from rest_framework.renderers import JSONRenderer
from decimal import Decimal
from ledgergw.serialisers import ReportSerializer, SettlementReportSerializer, OracleSerializer
from ledgergw import utils as ledgergw_utils
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from django.core.exceptions import ValidationError
from datetime import datetime
import base64
import traceback
import json
import ipaddress


@csrf_exempt
def user_info_search(request, apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            keyword = request.POST.get('keyword', '')
            jsondata = {'status': 200, 'message': 'No Results'}
            jsondata['users'] = [] 
            ledger_user_json = {}
            search_filter = Q()
            query_str_split = keyword.split(" ")
            search_filter |= Q(email__icontains=keyword.lower())
        
            #search_filter |= Q(first_name__icontains=query_str_split[0].lower())
            if len(query_str_split) == 1:
                  search_filter |= Q(first_name__icontains=query_str_split[0].lower())
            if len(query_str_split) > 1:
                  search_filter |= Q(Q(first_name__icontains=query_str_split[0].lower()) & Q(last_name__icontains=query_str_split[1].lower()))
            #for se_wo in query_str_split:
            #     
            #     search_filter |= Q(first_name__icontains=se_wo.lower()) | Q(last_name__icontains=se_wo.lower())

            ledger_users = models.EmailUser.objects.filter(search_filter)[:20]
            #,last_name__icontains=keyword)
            for ledger_obj in ledger_users:

                    ledger_user_json = {}
                    #if keyword.lower() in ledger_obj.first_name.lower()+' '+ledger_obj.last_name.lower() or keyword.lower() in ledger_obj.email.lower():
                    ledger_user_json['ledgerid'] = ledger_obj.id
                    ledger_user_json['email'] = ledger_obj.email
                    ledger_user_json['first_name'] = ledger_obj.first_name
                    ledger_user_json['last_name'] = ledger_obj.last_name
                    ledger_user_json['is_staff'] = ledger_obj.is_staff
                    ledger_user_json['is_superuser'] = ledger_obj.is_superuser
                    ledger_user_json['is_active'] = ledger_obj.is_active
                    ledger_user_json['date_joined'] = ledger_obj.date_joined.strftime('%d/%m/%Y %H:%M')
                    ledger_user_json['title'] = ledger_obj.title
                    if ledger_obj.dob:
                        ledger_user_json['dob'] = ledger_obj.dob.strftime('%d/%m/%Y %H:%M')
                    else:
                        ledger_user_json['dob'] = None
                    ledger_user_json['phone_number'] = ledger_obj.phone_number
                    ledger_user_json['position_title'] = ledger_obj.position_title
                    ledger_user_json['mobile_number'] = ledger_obj.mobile_number
                    ledger_user_json['fax_number'] = ledger_obj.fax_number
                    ledger_user_json['organisation'] = ledger_obj.organisation
                    #ledger_user_json['identification'] = ledger_obj.identification
                    #ledger_user_json['senior_card'] = ledger_obj.senior_card
                    ledger_user_json['character_flagged'] = ledger_obj.character_flagged
                    ledger_user_json['character_comments'] = ledger_obj.character_comments
                    ledger_user_json['extra_data'] = ledger_obj.extra_data
                    ledger_user_json['fullname'] = ledger_obj.get_full_name()
                    if ledger_obj.dob:
                        ledger_user_json['fullnamedob'] = ledger_obj.get_full_name_dob()
                    else:
                        ledger_user_json['fullnamedob'] = None
                    # Groups
                    #ledger_user_group = []
                    #for g in ledger_obj.groups.all():
                    #    ledger_user_group.append({'group_id': g.id, 'group_name': g.name})
                    #ledger_user_json['groups'] = ledger_user_group

                    jsondata['users'].append(ledger_user_json)
                    jsondata['status'] = 200
                    jsondata['message'] = 'Results'

        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    return HttpResponse(json.dumps(jsondata), content_type='application/json')

@csrf_exempt
def update_user_info_id(request, userid,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    
    post_list = list(request.POST)
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            ledger_user = models.EmailUser.objects.filter(id=int(userid))

            if ledger_user.count() > 0:
                ledger_obj = ledger_user[0]
                residential_address_obj = {}
                postal_address_obj = {}
                if 'residential_address' in post_list:
                    residential_address_obj = json.loads(request.POST.get('residential_address'))
                if 'postal_address' in post_list:
                    postal_address_obj = json.loads(request.POST.get('postal_address'))
                if 'dob' in post_list:
                    dob = request.POST.get('dob')
                    date_dob = datetime.strptime(dob, '%d/%m/%Y').date()
                    ledger_obj.dob = date_dob
                if 'residential_address' in post_list:
                    if ledger_obj.residential_address is None:
                        residential_address =  models.Address.objects.create(user=ledger_obj,
                                                  line1=residential_address_obj['residential_line1'],
                                                  locality=residential_address_obj['residential_locality'],
                                                  state=residential_address_obj['residential_state'],
                                                  postcode=residential_address_obj['residential_postcode'],
                                                  country=residential_address_obj['residential_country'],
                                                 )
                        ledger_obj.residential_address = residential_address
                    else:
                        if 'residential_line1' in residential_address_obj:
                               ledger_obj.residential_address.line1 =residential_address_obj['residential_line1']
                        if 'residential_locality' in residential_address_obj:
                               ledger_obj.residential_address.locality = residential_address_obj['residential_locality']
                        if 'residential_state' in residential_address_obj:
                               ledger_obj.residential_address.state = residential_address_obj['residential_state']
                        if 'residential_postcode' in residential_address_obj:
                               ledger_obj.residential_address.postcode = residential_address_obj['residential_postcode']
                        if 'residential_country' in residential_address_obj:
                               ledger_obj.residential_address.country = residential_address_obj['residential_country']
                        ledger_obj.residential_address.save()

                if 'postal_address' in post_list: 
                    if ledger_obj.postal_address is None:
                        postal_address =  models.Address.objects.create(user=ledger_obj,
                                                  line1=request.POST.get('postal_line1'),
                                                  locality=request.POST.get('postal_locality'),
                                                  state=request.POST.get('postal_state'),
                                                  postcode=request.POST.get('postal_postcode'),
                                                  country=request.POST.get('postal_country'),
                                                 )
                        ledger_obj.postal_address = postal_address
                    else:
                        if 'postal_line1' in postal_address_obj:
                            ledger_obj.postal_address.line1 =postal_address_obj['postal_line1']
                        if 'postal_locality' in postal_address_obj:
                               ledger_obj.postal_address.locality = postal_address_obj['postal_locality']
                        if 'postal_state' in postal_address_obj:
                               ledger_obj.postal_address.state = postal_address_obj['postal_state']
                        if 'postal_postcode' in postal_address_obj:
                               ledger_obj.postal_address.postcode = postal_address_obj['postal_postcode']
                        if 'postal_country' in postal_address_obj:
                               ledger_obj.postal_address.country = postal_address_obj['postal_country']
                        if 'postal_same_as_residential' in postal_address_obj:
                               ledger_obj.postal_same_as_residential = postal_address_obj['postal_same_as_residential']
                        ledger_obj.postal_address.save()
                if 'phone_number' in post_list:
                    ledger_obj.phone_number = request.POST.get('phone_number')

                if 'mobile_number' in post_list:
                    ledger_obj.mobile_number = request.POST.get('mobile_number')

                ledger_obj.save()
                #jsondata['user'] = ledger_user_json
                jsondata['status'] = 200
                jsondata['message'] = 'User updated'
            else:
                jsondata['status'] = '404'
                jsondata['message'] = 'User not found'
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    return HttpResponse(json.dumps(jsondata), content_type='application/json')

@csrf_exempt
def user_info_id(request, userid,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:

            ledger_user = models.EmailUser.objects.filter(id=int(userid))
            if ledger_user.count() > 0:
                    ledger_obj = ledger_user[0]
                    ledger_user_json['ledgerid'] = ledger_obj.id
                    ledger_user_json['email'] = ledger_obj.email
                    ledger_user_json['first_name'] = ledger_obj.first_name
                    ledger_user_json['last_name'] = ledger_obj.last_name
                    ledger_user_json['is_staff'] = ledger_obj.is_staff
                    ledger_user_json['is_superuser'] = ledger_obj.is_superuser
                    ledger_user_json['is_active'] = ledger_obj.is_active
                    ledger_user_json['date_joined'] = ledger_obj.date_joined.strftime('%d/%m/%Y %H:%M')
                    ledger_user_json['title'] = ledger_obj.title
                    if ledger_obj.dob:
                        ledger_user_json['dob'] = ledger_obj.dob.strftime('%d/%m/%Y')
                    else:
                        ledger_user_json['dob'] = None
                    ledger_user_json['phone_number'] = ledger_obj.phone_number
                    ledger_user_json['position_title'] = ledger_obj.position_title
                    ledger_user_json['mobile_number'] = ledger_obj.mobile_number
                    ledger_user_json['fax_number'] = ledger_obj.fax_number
                    ledger_user_json['organisation'] = ledger_obj.organisation
                    #ledger_user_json['identification'] = ledger_obj.identification
                    #ledger_user_json['senior_card'] = ledger_obj.senior_card
                    ledger_user_json['character_flagged'] = ledger_obj.character_flagged
                    ledger_user_json['character_comments'] = ledger_obj.character_comments
                    ledger_user_json['extra_data'] = ledger_obj.extra_data
                    ledger_user_json['fullname'] = ledger_obj.get_full_name()
                    if ledger_obj.dob:
                        ledger_user_json['fullnamedob'] = ledger_obj.get_full_name_dob()
                    else:
                        ledger_user_json['fullnamedob'] = None
                    ledger_user_json['residential_address'] =  {}
                    ledger_user_json['residential_address']['line1'] = ""
                    ledger_user_json['residential_address']['line2'] = ""
                    ledger_user_json['residential_address']['line3'] = ""
                    ledger_user_json['residential_address']['locality'] = ""
                    ledger_user_json['residential_address']['state'] = ""
                    ledger_user_json['residential_address']['country'] = ""
                    ledger_user_json['residential_address']['postcode'] = ""
                    if ledger_obj.residential_address:
                         ledger_user_json['residential_address']['line1'] = ledger_obj.residential_address.line1
                         ledger_user_json['residential_address']['line2'] = ledger_obj.residential_address.line2
                         ledger_user_json['residential_address']['line3'] = ledger_obj.residential_address.line3
                         ledger_user_json['residential_address']['locality'] = ledger_obj.residential_address.locality
                         ledger_user_json['residential_address']['state'] = ledger_obj.residential_address.state
                         if ledger_obj.residential_address.country:
                             ledger_user_json['residential_address']['country'] = ledger_obj.residential_address.country.code
                         ledger_user_json['residential_address']['postcode'] = ledger_obj.residential_address.postcode

                    ledger_user_json['postal_address'] = {}
                    ledger_user_json['postal_address']['line1'] = ""
                    ledger_user_json['postal_address']['line2'] = ""
                    ledger_user_json['postal_address']['line3'] = ""
                    ledger_user_json['postal_address']['locality'] = ""
                    ledger_user_json['postal_address']['state'] = ""
                    ledger_user_json['postal_address']['country'] = ""
                    ledger_user_json['postal_address']['postcode'] = ""

                    if ledger_obj.postal_address:
                         ledger_user_json['postal_address']['line1'] = ledger_obj.postal_address.line1
                         ledger_user_json['postal_address']['line2'] = ledger_obj.postal_address.line2
                         ledger_user_json['postal_address']['line3'] = ledger_obj.postal_address.line3
                         ledger_user_json['postal_address']['locality'] = ledger_obj.postal_address.locality
                         ledger_user_json['postal_address']['state'] = ledger_obj.postal_address.state
                         ledger_user_json['postal_address']['country'] = ""
                         if ledger_obj.postal_address.country:
                             ledger_user_json['postal_address']['country'] = ledger_obj.postal_address.country.code
                         ledger_user_json['postal_address']['postcode'] = ledger_obj.postal_address.postcode
                    ledger_user_json['postal_same_as_residential'] = ledger_obj.postal_same_as_residential
                         

                    # Groups
                    ledger_user_group = []
                    for g in ledger_obj.groups.all():
                        ledger_user_group.append({'group_id': g.id, 'group_name': g.name})
                    ledger_user_json['groups'] = ledger_user_group
                    jsondata['user'] = ledger_user_json
                    jsondata['status'] = 200
                    jsondata['message'] = 'User Found'
            else:
                jsondata['status'] = '404'
                jsondata['message'] = 'User not found'
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    return HttpResponse(json.dumps(jsondata), content_type='application/json')


@csrf_exempt
def user_info(request, ledgeremail,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            ledgeremail=ledgeremail.lower()
            ledgeremail=ledgeremail.replace(" ","")
            ledger_user = models.EmailUser.objects.filter(email=ledgeremail)
            if ledger_user.count() == 0:
                 first_name = request.POST.get('first_name','')
                 last_name =  request.POST.get('last_name','')
                 a = models.EmailUser.objects.create(email=ledgeremail,first_name=first_name,last_name=last_name)
                 #a.save()
                 #ledger_user = models.EmailUser.objects.filter(email=ledgeremail)
                 #ledger_user.save()


            if ledger_user.count() > 0:
                    ledger_obj = ledger_user[0]
                    ledger_user_json['ledgerid'] = ledger_obj.id
                    ledger_user_json['email'] = ledger_obj.email
                    ledger_user_json['first_name'] = ledger_obj.first_name
                    ledger_user_json['last_name'] = ledger_obj.last_name
                    ledger_user_json['is_staff'] = ledger_obj.is_staff
                    ledger_user_json['is_superuser'] = ledger_obj.is_superuser
                    ledger_user_json['is_active'] = ledger_obj.is_active
                    ledger_user_json['date_joined'] = ledger_obj.date_joined.strftime('%d/%m/%Y %H:%M')
                    ledger_user_json['title'] = ledger_obj.title
                    if ledger_obj.dob:
                        ledger_user_json['dob'] = ledger_obj.dob.strftime('%d/%m/%Y %H:%M')
                    else:
                        ledger_user_json['dob'] = None
                    ledger_user_json['phone_number'] = ledger_obj.phone_number
                    ledger_user_json['position_title'] = ledger_obj.position_title
                    ledger_user_json['mobile_number'] = ledger_obj.mobile_number
                    ledger_user_json['fax_number'] = ledger_obj.fax_number
                    ledger_user_json['organisation'] = ledger_obj.organisation
                    #ledger_user_json['residential_address'] =  {}
                    #if ledger_obj.residential_address:
                    #     ledger_user_json['residential_address']['line1'] = ledger_obj.residential_address.line1 

                    #ledger_user_json['residential_address'] = ledger_obj.residential_address
                    #ledger_user_json['postal_address'] = ledger_obj.postal_address
                    #ledger_user_json['billing_address'] = ledger_obj.billing_address
                    #ledger_user_json['identification'] = ledger_obj.identification
                    #ledger_user_json['senior_card'] = ledger_obj.senior_card
                    ledger_user_json['character_flagged'] = ledger_obj.character_flagged
                    ledger_user_json['character_comments'] = ledger_obj.character_comments
                    ledger_user_json['extra_data'] = ledger_obj.extra_data
                    ledger_user_json['fullname'] = ledger_obj.get_full_name()
                    if ledger_obj.dob:
                        ledger_user_json['fullnamedob'] = ledger_obj.get_full_name_dob()
                    else:
                        ledger_user_json['fullnamedob'] = None
                    # Groups
                    ledger_user_group = []
                    for g in ledger_obj.groups.all():
                        ledger_user_group.append({'group_id': g.id, 'group_name': g.name})
                    ledger_user_json['groups'] = ledger_user_group
                    jsondata['user'] = ledger_user_json
                    jsondata['status'] = 200
                    jsondata['message'] = 'User Found'
            else:
                jsondata['status'] = '404'
                jsondata['message'] = 'User not found'
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    return HttpResponse(json.dumps(jsondata), content_type='application/json')



@csrf_exempt
def user_group_info(request, ledger_id,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    query_exists = False
    ledger_user_json  = {}
    filter_post = json.loads(request.POST['filter'])
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            ledger_user = models.EmailUser.objects.filter(id=ledger_id)
            if ledger_user.count() > 0:
                    ledger_obj = ledger_user[0]
                    ledger_user_group = []
                    if len(filter_post) > 0: 
                        if 'name' in filter_post:
                            query = ledger_obj.groups.filter(name=filter_post['name'])
                            for g in query:
                                  ledger_user_group.append({'group_id': g.id, 'group_name': g.name})
                        if 'id' in filter_post:
                            query = ledger_obj.groups.filter(id=int(filter_post['id']))
                            for g in query:
                                ledger_user_group.append({'group_id': g.id, 'group_name': g.name})
                        if 'name' in filter_post and 'id' in filter_post:
                            query = ledger_obj.groups.filter(name=filter_post['name'], id=int(filter_post['id']))
                            for g in query:
                                ledger_user_group.append({'group_id': g.id, 'group_name': g.name})
                        query_exists = query.exists()

                    else:
                        for g in ledger_obj.groups.all():
                             ledger_user_group.append({'group_id': g.id, 'group_name': g.name})
                    ledger_user_json['groups'] = ledger_user_group
                    jsondata['groups'] = ledger_user_json
                    jsondata['query_exists'] = query_exists
                    jsondata['status'] = 200
                    jsondata['message'] = 'User Found'
            else:
                jsondata['status'] = '404'
                jsondata['message'] = 'User not found'
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    return HttpResponse(json.dumps(jsondata), content_type='application/json')


def group_info(request, apikey):
    ledger_json  = {}
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            groups = Group.objects.all()
            ledger_json['groups_list'] = []
            ledger_json['groups_id_map'] = {}
            ledger_json['groups_name_map'] = {}
            for g in groups:
                ledger_json['groups_list'].append({'group_id': g.id,'group_name': g.name})
                ledger_json['groups_id_map'][g.id] = g.name
                ledger_json['groups_name_map'][g.name] = g.id

            jsondata['groups_list'] = ledger_json['groups_list']
            jsondata['groups_id_map'] = ledger_json['groups_id_map']
            jsondata['groups_name_map'] = ledger_json['groups_name_map']

            jsondata['status'] = 200
            jsondata['message'] = 'Groups Retreived'

        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'

    return HttpResponse(json.dumps(jsondata), content_type='application/json')


@csrf_exempt
def add_update_file_emailuser(request, apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            emailuser_id = request.POST.get('emailuser_id', '')
            file_group_id = request.POST.get('file_group_id', None)
            filebase64 = request.POST['filebase64']
            extension = request.POST.get('extension',None)

            randomfile_name = get_random_string(length=15, allowed_chars=u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            b64data = filebase64.split(",") 
            cfile = ContentFile(base64.b64decode(b64data[1]), name=randomfile_name+'.'+extension)
            private_document = models.PrivateDocument.objects.create(upload=cfile,name=randomfile_name,file_group=file_group_id,file_group_ref_id=emailuser_id,extension=extension)
            email_user = models.EmailUser.objects.get(id=emailuser_id)
            if int(file_group_id) == 1:
               email_user.identification2=private_document
               email_user.save()
            if int(file_group_id) == 2:
               email_user.senior_card2=private_document
               email_user.save()
            
            jsondata = {'status': 200, 'message': 'Results',}
        else:
           jsondata['status'] = 403
           jsondata['message'] = 'Access Forbidden'

    return HttpResponse(json.dumps(jsondata), content_type='application/json')

@csrf_exempt
def get_private_document(request, apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            private_document_id = request.POST.get('private_document_id', None)
            private_document = models.PrivateDocument.objects.get(id=private_document_id)

            #print (private_document.upload.path)
            with open(private_document.upload.path, "rb") as doc:
                 encoded_doc = base64.b64encode(doc.read())
            #print (encoded_doc)
            jsondata = {'status': 200, 'message': 'Results','data': encoded_doc.decode(), 'filename': private_document.name, 'extension': private_document.extension}
        else:
           jsondata['status'] = 403
           jsondata['message'] = 'Access Forbidden'

    return HttpResponse(json.dumps(jsondata), content_type='application/json')



@csrf_exempt
def create_basket_session(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            print ("API create_basket_session")
            parameters = json.loads(request.POST.get('parameters', "{}"))
            emailuser_id = request.POST.get('emailuser_id', None)
            basket, basket_hash = utils.create_basket_session_v2(emailuser_id,parameters)
            jsondata['status'] = 200
            jsondata['message'] = 'Success'
            jsondata['data'] = {'basket_hash': basket_hash}
            #ledger_user = models.EmailUser.objects.filter(email=ledgeremail)
            #if ledger_user.count() == 0:

            #     a = models.EmailUser.objects.create(email=ledgeremail,first_name=request.POST['first_name'],last_name=request.POST['last_name'])
            #     ledger_user = models.EmailUser.objects.filter(email=ledgeremail)
            #     ledger_user.save()
            #else:
            #    jsondata['status'] = '404'
            #    jsondata['message'] = 'User not found'
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    return HttpResponse(json.dumps(jsondata), content_type='application/json')


@csrf_exempt
def create_checkout_session(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            print ("API create_basket_session")
            checkout_parameters = json.loads(request.POST.get('checkout_parameters', "{}"))
            #emailuser_id = request.POST.get('emailuser_id', None)
            #print (emailuser_id)
            resp = utils.create_checkout_session(request,checkout_parameters)
            #basket, basket_hash = utils.create_checkout_session(request, parameters)
            jsondata['status'] = 200
            jsondata['message'] = 'Success'
            jsondata['data'] = {}
            #jsondata['data'] = {'basket_hash': basket_hash}

            #ledger_user = models.EmailUser.objects.filter(email=ledgeremail)
            #if ledger_user.count() == 0:

            #     a = models.EmailUser.objects.create(email=ledgeremail,first_name=request.POST['first_name'],last_name=request.POST['last_name'])
            #     ledger_user = models.EmailUser.objects.filter(email=ledgeremail)
            #     ledger_user.save()
            #else:
            #    jsondata['status'] = '404'
            #    jsondata['message'] = 'User not found'
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    response.set_cookie('CookieTest', 'Testing',5)
    return response

@csrf_exempt
def get_order_info(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            print ("API get_order_info")
            data = json.loads(request.POST.get('data', "{}"))
            if 'basket_id' in data:
               order = Order.objects.get(basket__id=data['basket_id'])
            if 'number' in data:
               order = Order.objects.get(number=data['number'])
            order_obj = {}
            order_obj['id'] = order.id
            order_obj['number'] = order.number
            #order_obj['owner'] = order.owner
            order_obj['user_id'] = None
            if order.user:
                 order_obj['user_id'] = order.user.id

            jsondata['status'] = 200
            jsondata['message'] = 'Success'
            jsondata['data'] = {'order': order_obj}
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    response.set_cookie('CookieTest', 'Testing',5)
    return response

@csrf_exempt
def get_order_lines(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            print ("API get_order_line")
            data = json.loads(request.POST.get('data', "{}"))
            order = []
            order_obj = []

            if 'number' in data:
                order_info = order_models.Order.objects.filter(number=data['number'])
                if order_info.count() > 0:
                     order = order_models.Line.objects.filter(order=order_info[0])#,oracle_code=data['oracle_code'])

            if 'order_id' in data:
                order = order_models.Line.objects.filter(order_id=data['order_id'])
            for o in order:
               row = {}
               row['id'] = o.id
               row['title'] = o.title
               row['oracle_code'] = o.oracle_code
               row['quantity'] = o.quantity
               row['price_incl_tax'] = str(o.line_price_incl_tax)
               row['price_excl_tax'] = str(o.line_price_excl_tax)
               row['paid'] = str(o.paid)
               row['unit_price_incl_tax'] = str(o.unit_price_incl_tax)
               row['unit_price_excl_tax'] = str(o.unit_price_excl_tax)

               order_obj.append(row)
            jsondata['status'] = 200
            jsondata['message'] = 'Success'
            jsondata['data'] = {'orderlines': order_obj}
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    response.set_cookie('CookieTest', 'Testing',5)
    return response



#is = ledger_payments_models.OracleInterfaceSystem.objects.filter(system_id=system_id_zeroed,enabled=True),

def get_failed_refund_totals(request,apikey,system_id):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            ois_obj = {}
            total_fr = payment_models.RefundFailed.objects.filter(system_identifier__system_id=system_id).count()
            jsondata['status'] = 200
            jsondata['message'] = 'Success'
            jsondata['data'] = {'total_failed': total_fr}
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    response.set_cookie('CookieTest', 'Testing',5)
    return response

@csrf_exempt
def oracle_interface_system(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    ledger_user_json  = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            ois_obj = {}
            data = json.loads(request.POST.get('data', "{}"))
            ois = payment_models.OracleInterfaceSystem.objects.filter(system_id=system_id_zeroed,enabled=True)
            if ois.count() > 0:
                ois_obj['system_id'] = ois[0].system_id
                ois_obj['system_name'] = ois[0].system_name
                ois_obj['enabled'] = ois[0].enabled
                ois_obj['integration_type'] = ois[0].integration_type

            jsondata['status'] = 200
            jsondata['message'] = 'Success'
            jsondata['data'] = {'ois': ois_obj}
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    response.set_cookie('CookieTest', 'Testing',5)
    return response


@csrf_exempt
def get_invoice_properties(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    invoice_json = {}
    print ("API get_invoice_properties 1") 
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            print ("API get_invoice_properties 2")
            data = json.loads(request.POST.get('data', "{}"))
            print (data)
            if Invoice.objects.filter(id=data['invoice_id']).count() > 0:
                 try:
                       invoice = Invoice.objects.get(id=data['invoice_id'])
                       invoice_obj = {}
                       invoice_obj['id'] = invoice.id
                       invoice_obj['text'] = invoice.text
                       invoice_obj['amount'] = str(invoice.amount)
                       invoice_obj['order_number'] = invoice.order_number
                       invoice_obj['reference'] = invoice.reference
                       invoice_obj['system'] = invoice.system
                       invoice_obj['token'] = invoice.token
                       invoice_obj['voided'] = invoice.voided
                       invoice_obj['previous_invoice'] = invoice.previous_invoice
                       invoice_obj['settlement_date'] = invoice.settlement_date.strftime('%d/%m/%Y')
                       invoice_obj['payment_method'] = invoice.payment_method
                       invoice_obj['biller_code'] = invoice.biller_code
                       invoice_obj['number'] = invoice.number
                       if invoice.owner:
                           invoice_obj['owner'] = invoice.owner.id
                       else:
                           invoice_obj['owner'] = None
                       invoice_obj['refundable_amount'] = str(invoice.refundable_amount)
                       invoice_obj['refundable'] = invoice.refundable
                       invoice_obj['num_items'] = invoice.num_items
                       #invoice_obj['linked_bpay_transactions'] = invoice.linked_bpay_transactions

                       invoice_obj['payment_amount'] = str(invoice.payment_amount)
                       invoice_obj['total_payment_amount'] = str(invoice.total_payment_amount)
                       invoice_obj['refund_amount'] = str(invoice.refund_amount)
                       invoice_obj['deduction_amount'] = str(invoice.deduction_amount)
                       invoice_obj['transferable_amount'] = str(invoice.transferable_amount)
                       invoice_obj['balance'] = str(invoice.balance)
                       invoice_obj['payment_status'] = invoice.payment_status

                       jsondata['status'] = 200
                       jsondata['message'] = 'Success'
                       jsondata['data'] = {'invoice': invoice_obj}
                       print ("YES")
                 except Exception as e:
                     print (e)
                     print ("ERROR")
            else:
                 jsondata['status'] = 404
                 jsondata['message'] = 'not found'
                 jsondata['data'] = {'invoice': None}
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    return response

def get_linked_invoice_data_by_booking_reference(booking_reference, system_id):
    linked_payment_data = {}
    ois = payment_models.OracleInterfaceSystem.objects.get(system_id=system_id)
    li = payment_models.LinkedInvoice.objects.filter(booking_reference=booking_reference,system_identifier=ois)
    if li.count() > 0:
        invoice_group_id = li[0].invoice_group_id
        linked_payment_data = get_linked_invoice_data(invoice_group_id,system_id)
    return linked_payment_data

def get_linked_invoice_data(invoice_group_id, system_id):
    linked_payment_data = {'total_available': '0.00', 'txn_pool': {}}
    invoice_array = []
    total_available = Decimal('0.00')
    ois = payment_models.OracleInterfaceSystem.objects.get(system_id=system_id)
    li = payment_models.LinkedInvoice.objects.filter(invoice_group_id=invoice_group_id,system_identifier=ois)
    for lp in li:
        if lp.invoice_reference not in invoice_array:
            invoice_array.append(lp.invoice_reference)
    bp_trans = payment_bpoint_models.BpointTransaction.objects.filter(crn1__in=invoice_array)
    for bp in bp_trans:
        if bp.action == 'payment':
            if bp.txn_number not in linked_payment_data['txn_pool']:
                linked_payment_data['txn_pool'][bp.txn_number] = Decimal('0.00')

            total_available = total_available + bp.amount
            linked_payment_data['txn_pool'][bp.txn_number] = linked_payment_data['txn_pool'][bp.txn_number] + bp.amount

        if bp.action == 'refund':
            if bp.original_txn not in linked_payment_data['txn_pool']:
                linked_payment_data['txn_pool'][bp.original_txn] = Decimal('0.00')

            total_available = total_available - bp.amount
            linked_payment_data['txn_pool'][bp.original_txn] = linked_payment_data['txn_pool'][bp.original_txn] - bp.amount
    linked_payment_data['total_available'] = str(total_available)
    return linked_payment_data

def basket_totals(basket_id):
    basket_obj = basket_models.Line.objects.filter(basket_id=basket_id)
    basket_total = Decimal('0.00')
    if basket_obj.count() > 0:
        try:
            for b in basket_obj:
                basket_total = basket_total + (b.price_incl_tax * b.quantity)
        except:
            print("Error Totaling Basket")
    return basket_total

@csrf_exempt
def get_basket_total(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    invoice_json = {}
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
                 data = json.loads(request.POST.get('data', "{}"))
                 try:
                       basket_total = basket_totals(data['basket_id'])
                       jsondata['status'] = 200
                       jsondata['message'] = 'Success'
                       jsondata['data'] = {'basket_total': str(basket_total)}
                 except:
                       jsondata['status'] = 500
                       jsondata['message'] = "Basket Total Error"
                       jsondata['data'] = {}
        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    return response

@csrf_exempt
def process_api_refund(request,apikey):
    print ("process_api_refund 1")
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    invoice_json = {}
    basket =None
    failed_refund = False
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
         if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
             data = json.loads(request.POST.get('data', "{}")) 
             basket_params = json.loads(request.POST.get("basket_parameters","{}"))
             customer_id = json.loads(request.POST.get("customer_id", None))
             return_url = request.POST.get("return_url", None)
             return_preload_url = request.POST.get("return_preload_url", None)
             user_logged_in  = request.POST.get("user_logged_in", None)

             customer = models.EmailUser.objects.get(id=customer_id)
             basket, basket_hash = utils.create_basket_session_v2(customer_id, basket_params)
             basket_obj = basket_models.Basket.objects.filter(id=basket.id)
             request.basket = basket_obj[0]
             system_id = basket.system.replace('S','0')
             booking_reference = basket.booking_reference_link
             basket_total = basket_totals(basket.id)
             # create checkout session

             checkout_params = {
                 'system': basket.system,
                 'fallback_url': request.build_absolute_uri('/'),
                 'return_url': return_url,
                 'return_preload_url': return_preload_url,
                 'force_redirect': True,
                 'proxy':  False,
                 'invoice_text': "Refund via system",
                 'session_type' : 'ledger_api',
                 'user_logged_in' : int(user_logged_in)
                 #'amount_override': float('1.00')
             }

             resp = utils.create_checkout_session(request,checkout_params)
             jsondata = process_refund_from_basket(request,basket_obj)
         else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    return response

def process_refund_from_basket(request,basket_obj):
            jsondata = {'status': 404, 'message': 'No basket'}
            linked_payment_data = None
            basket_total = Decimal('0.00')
            basket = None
            system_id = None
            booking_reference = None

            if basket_obj.count() > 0:
                basket=basket_obj[0]
                basket_total = basket_totals(basket.id)
                basket.save()
                system_id = basket_obj[0].system.replace('S','0')
                booking_reference = basket_obj[0].booking_reference_link
                linked_payment_data = get_linked_invoice_data_by_booking_reference(booking_reference,system_id)
            basket_total_positive = basket_total - basket_total - basket_total
            refund_tx_pool = {}
            #basket_total_positive = Decimal('730.00')
            if basket_total_positive > Decimal(linked_payment_data['total_available']):
                print ("ERROR,  Not enough funds")
                return
            for tx in linked_payment_data['txn_pool']:
                txn_avail = linked_payment_data['txn_pool'][tx] - basket_total_positive
                if txn_avail >= 0:
                    refund_tx_pool[tx] = basket_total_positive
                    basket_total_positive = basket_total_positive - basket_total_positive
                if txn_avail < 0:
                    refund_tx_pool[tx] = (txn_avail + basket_total_positive)
                    basket_total_positive =  txn_avail - txn_avail - txn_avail
            # Prepare to send transactions to bpoint
            for tx in refund_tx_pool:
                if refund_tx_pool[tx] > 0:
                      print ('refunding for txpool --> '+tx+' with amount '+str(refund_tx_pool[tx]))
                      b_total =  Decimal('{:.2f}'.format(float(refund_tx_pool[tx])))
                      info = {'amount': Decimal('{:.2f}'.format(float(refund_tx_pool[tx]))), 'details' : 'Refund via system'}
                      invoice_reference=None
                      refund = None
                      invoice_reference=None
                      bpoint_obj=None
                      try:
                         bpoint_obj = payment_bpoint_models.BpointTransaction.objects.filter(txn_number=tx)
                         if bpoint_obj.count() > 0:
                               
                              bpoint = bpoint_obj[0]
                              invoice_reference=bpoint.crn1
                              
                              refund = bpoint.refund(info,basket.owner)
                              invoice_reference=bpoint.crn1
                              invoice = Invoice.objects.get(reference=bpoint.crn1)
                              payments_utils.update_payments(invoice.reference)
                      except Exception as e:
                         print ("EXCEPTION")
                         print (e)
                         failed_refund = True
                         system = payment_models.OracleInterfaceSystem.objects.get(system_id=system_id)
                         li = payment_models.LinkedInvoice.objects.filter(booking_reference=booking_reference,system_identifier=system)
                         payment_models.RefundFailed.objects.create(invoice_group=li[0].invoice_group_id,
                                                                    booking_reference=booking_reference,
                                                                    invoice_reference=invoice_reference,
                                                                    refund_amount=Decimal(refund_tx_pool[tx]),
                                                                    status=0,
                                                                    basket_json="{}",
                                                                    system_identifier=system,
                                                                   )
                         #booking_invoice = BookingInvoice.objects.filter(booking=booking.old_booking).order_by('id')
                         #for bi in booking_invoice:
                         #    invoice = Invoice.objects.get(reference=bi.invoice_reference)
                         #RefundFailed.objects.create(booking=booking, invoice_reference=invoice.reference, refund_amount=b_total,status=0)
                      order_response = None
                      try:
                          order_response = utils.place_order_submission(request)
                      except Exception as e:
                          print ("ORDER RESPONSE EXCEPTION")
                          print (e)

                      new_order = Order.objects.get(basket=basket)
                      new_order.user = basket.owner
                      new_order.save()
                      new_invoice = Invoice.objects.get(order_number=new_order.number)
                      new_invoice.settlement_date = None
                      new_invoice.save()
                      if refund:
                           invoice.voided = True
                           invoice.save()
                           bpoint_refund = payment_bpoint_models.BpointTransaction.objects.get(txn_number=refund.txn_number)
                           bpoint_refund.crn1 = new_invoice.reference
                           bpoint_refund.save()
                           payments_utils.update_payments(invoice.reference)
                      payments_utils.update_payments(new_invoice.reference)
                      if order_response:
                          jsondata['status'] = 200
                          jsondata['message'] = 'success'
                          jsondata['order_response'] = json.loads(order_response.content.decode("utf-8"))
                          jsondata['data'] = {'invoice_reference': new_invoice.reference}
                          #return order_response
                      else:
                         jsondata['status'] = 500
                         jsondata['message'] = 'error'
                         jsondata['order_response'] = {}
                         jsondata['data'] = {}
                      return jsondata



def process_zero(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    invoice_json = {}
    basket =None
    failed_refund = False
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            data = json.loads(request.POST.get('data', "{}"))
            basket_hash = request.COOKIES.get('ledgergw_basket','')
            basket_hash_split = basket_hash.split("|")
            basket_obj = basket_models.Basket.objects.filter(id=basket_hash_split[0])
            order_response = utils.place_order_submission(request)
            new_order = Order.objects.get(basket=basket_obj)
            new_invoice = Invoice.objects.get(order_number=new_order.number)

            if order_response:
                jsondata['status'] = 200
                jsondata['message'] = 'success'
                jsondata['order_response'] = json.loads(order_response.content.decode("utf-8"))
                #return order_response
            else:
               jsondata['status'] = 500
               jsondata['message'] = 'error'
               jsondata['order_response'] = {}
            #jsondata = process_refund_from_basket(request,basket_obj)

        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    return response


def process_no(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    invoice_json = {}
    basket =None
    failed_refund = False
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            data = json.loads(request.POST.get('data', "{}"))
            basket_hash = request.COOKIES.get('ledgergw_basket','')
            basket_hash_split = basket_hash.split("|")
            basket_obj = basket_models.Basket.objects.filter(id=basket_hash_split[0])
            order_response = utils.place_order_submission(request)
            new_order = Order.objects.get(basket=basket_obj)
            new_invoice = Invoice.objects.get(order_number=new_order.number)

            if order_response:
                jsondata['status'] = 200
                jsondata['message'] = 'success'
                jsondata['order_response'] = json.loads(order_response.content.decode("utf-8"))
                #return order_response
            else:
               jsondata['status'] = 500
               jsondata['message'] = 'error'
               jsondata['order_response'] = {}
            #jsondata = process_refund_from_basket(request,basket_obj)

        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    return response

def delete_card_token(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    invoice_json = {}
    basket =None
    failed_refund = False
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            data = json.loads(request.POST.get('data', "{}"))
            card_token_id = request.POST.get('card_token_id', None)
            user_logged_in = request.POST.get('user_logged_in', None)
            PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE = request.POST.get('PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE',None)
            email_user_obj = models.EmailUser.objects.filter(id=int(user_logged_in))
            user = None
            if email_user_obj.count() > 0:
                user=email_user_obj[0]
            
            bt = BpointToken.objects.filter(user=user,id=int(card_token_id),system_id=PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE)
            if bt.count() > 0:
                for b in bt:
                    b.delete()
                jsondata['status'] = 200
                jsondata['message'] = 'success'

             
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    return response
             

def get_card_tokens_for_user(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    
    basket =None
    failed_refund = False
    card_tokens = []

    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            data = json.loads(request.POST.get('data', "{}"))
            user_logged_in = request.POST.get('user_logged_in', None)
            PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE = request.POST.get('PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE',None)
            email_user_obj = models.EmailUser.objects.filter(id=int(user_logged_in))
            user = None
            if email_user_obj.count() > 0:
                user=email_user_obj[0]

            bt = BpointToken.objects.filter(user=user,system_id=PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE)
            if bt.count() > 0:
                for b in bt:
                    card_tokens.append({'id' : b.id,  'last_digits' : b.last_digits,'expiry_date' : b.expiry_date.strftime("%m/%y"), 'card_type' : b.get_card_type_display()})

            jsondata['card_tokens'] = card_tokens
            jsondata['status'] = 200
            jsondata['message'] = 'success'


 
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    return response


def process_refund(request,apikey):
    jsondata = {'status': 404, 'message': 'API Key Not Found'}
    invoice_json = {}
    basket =None
    failed_refund = False
    if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
        if ledgerapi_utils.api_allow(ledgerapi_utils.get_client_ip(request),apikey) is True:
            data = json.loads(request.POST.get('data', "{}"))
            basket_hash = request.COOKIES.get('ledgergw_basket','')
            basket_hash_split = basket_hash.split("|")
            basket_obj = basket_models.Basket.objects.filter(id=basket_hash_split[0])
            jsondata = process_refund_from_basket(request,basket_obj)
            #return resp
            #linked_payment_data = None
            #if basket_obj.count() > 0:
            #    basket=basket_obj[0]
            #    basket.save()
            #    system_id = basket_obj[0].system.replace('S','0')
            #    booking_reference = basket_obj[0].booking_reference_link
            #    linked_payment_data = get_linked_invoice_data_by_booking_reference(booking_reference,system_id)
            #basket_total_positive = basket_total - basket_total - basket_total 
            #refund_tx_pool = {}
            ##basket_total_positive = Decimal('730.00')

            #if basket_total_positive > Decimal(linked_payment_data['total_available']):
            #    print ("ERROR,  Not enough funds")
            #    return
            #for tx in linked_payment_data['txn_pool']:
            #    txn_avail = linked_payment_data['txn_pool'][tx] - basket_total_positive
            #    if txn_avail > 0:
            #        refund_tx_pool[tx] = basket_total_positive
            #        basket_total_positive = basket_total_positive - basket_total_positive 
            #    if txn_avail < 0:
            #        refund_tx_pool[tx] = (txn_avail + basket_total_positive)
            #        basket_total_positive =  txn_avail - txn_avail - txn_avail


            ## Prepare to send transactions to bpoint        
            #for tx in refund_tx_pool:
            #    if refund_tx_pool[tx] > 0:
            #          print ('refunding for txpool --> '+tx+' with amount '+str(refund_tx_pool[tx]))                      
            #          b_total =  Decimal('{:.2f}'.format(float(refund_tx_pool[tx])))
            #          info = {'amount': Decimal('{:.2f}'.format(float(refund_tx_pool[tx]))), 'details' : 'Refund via system'}
            #          try:
            #             bpoint_obj = payment_bpoint_models.BpointTransaction.objects.filter(txn_number=tx)
            #             if bpoint_obj.count() > 0:
            #                  bpoint = bpoint_obj[0]
            #                  refund = bpoint.refund(info,basket.owner)
            #                  invoice = Invoice.objects.get(reference=bpoint.crn1)
            #                  payments_utils.update_payments(invoice.reference)
            #          except Exception as e:
            #             print (e)
            #             failed_refund = True
            #             #booking_invoice = BookingInvoice.objects.filter(booking=booking.old_booking).order_by('id')
            #             #for bi in booking_invoice:
            #             #    invoice = Invoice.objects.get(reference=bi.invoice_reference)
            #             #RefundFailed.objects.create(booking=booking, invoice_reference=invoice.reference, refund_amount=b_total,status=0)
            #          order_response = None
            #          try:
            #              order_response = utils.place_order_submission(request)
            #          except Exception as e:
            #              print ("ORDER RESPONSE EXCEPTION")
            #              print (e)

            #          new_order = Order.objects.get(basket=basket)
            #          new_invoice = Invoice.objects.get(order_number=new_order.number)
            #          new_invoice.settlement_date = None
            #          new_invoice.save()
            #          if refund:
            #               invoice.voided = True
            #               invoice.save()
            #               bpoint_refund = payment_bpoint_models.BpointTransaction.objects.get(txn_number=refund.txn_number)
            #               bpoint_refund.crn1 = new_invoice.reference
            #               bpoint_refund.save()
            #               payments_utils.update_payments(invoice.reference)
            #          payments_utils.update_payments(new_invoice.reference)
            #          if order_response:
            #              jsondata['status'] = 200
            #              jsondata['message'] = 'success'
            #              jsondata['order_response'] = json.loads(order_response.content.decode("utf-8"))
                      #return order_response
            #basket = basket_models.Basket.objects.get(id=basket_hash_split[0])

            #print (basket)

        else:
            jsondata['status'] = 403
            jsondata['message'] = 'Access Forbidden'
    else:
        pass
    response = HttpResponse(json.dumps(jsondata), content_type='application/json')
    return response



def ip_check(request):
    ledger_json  = {}
    ipaddress = ledgerapi_utils.get_client_ip(request)
    jsondata = {'status': 200, 'ipaddress': str(ipaddress)}
    return HttpResponse(json.dumps(jsondata), content_type='application/json')


class SettlementReportView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        try:
            http_status = status.HTTP_200_OK
            # parse and validate data
            system = request.GET.get('system')
            report = None
            data = {
                "date": request.GET.get('date'),
            }
            serializer = SettlementReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'Settlement Report-{}'.format(str(serializer.validated_data['date']))
            # Generate Report
            report = reports.booking_bpoint_settlement_report(serializer.validated_data['date'],system)
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()


class RefundsReportView(views.APIView):
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        try:
            http_status = status.HTTP_200_OK
            # parse and validate data
            report = None
            system = request.GET.get('system')
            data = {
                "start": request.GET.get('start'),
                "end": request.GET.get('end'),
            }
            serializer = ReportSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            filename = 'Refunds Report-{}-{}'.format(str(serializer.validated_data['start']), str(serializer.validated_data['end']))
            # Generate Report
            report = reports.booking_refunds(serializer.validated_data['start'], serializer.validated_data['end'],system)
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            print (e)
            traceback.print_exc()


class OracleJob(views.APIView):
    renderer_classes = [JSONRenderer, ]

    def get(self, request, format=None):
        try:
            system = request.GET.get('system')
            data = {
                "date": request.GET.get("date"),
                "override": request.GET.get("override")
            }
            
            serializer = OracleSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            ledgergw_utils.oracle_integration(serializer.validated_data['date'].strftime('%Y-%m-%d'), serializer.validated_data['override'], system)
            data = {'successful': True}
            return Response(data)
        except serializers.ValidationError:
            print(traceback.print_exc())
            raise
        except ValidationError as e:
            raise serializers.ValidationError(repr(e.error_dict))
        except Exception as e:
            print(traceback.print_exc())
            raise serializers.ValidationError(str(e[0]))


def get_countries(request):
     resp = {'status': 404, 'data': {}, 'message': ''}
     countries_list = []
     countries = models.Country.objects.all() 
     for c in countries:
         countries_list.append({'country_name' : c.printable_name, 'country_code' : c.iso_3166_1_a2 })
     resp['data'] = countries_list
     return HttpResponse(json.dumps(resp), content_type='application/json')

