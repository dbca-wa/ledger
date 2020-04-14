from django.http import HttpResponse, JsonResponse
from ledger.accounts import models
import json

def user_info(request, ledgeremail):
    #booking_id = kwargs['pk']
    #booking = Booking.objects.get(pk=booking_id)
    #bpoint_id = None
    #return HttpResponse("WORKING")

    ledger_user_json  = {}
    jsondata = {}
    ledger_user = models.EmailUser.objects.filter(email=ledgeremail)
    if ledger_user.count() > 0:
            ledger_obj = ledger_user[0]
            ledger_user_json['ledgerid'] = ledger_obj.id
            ledger_user_json['email'] = ledger_obj.email
            ledger_user_json['first_name'] = ledger_obj.first_name
            ledger_user_json['last_name'] = ledger_obj.last_name
            ledger_user_json['is_staff'] = ledger_obj.is_staff
            ledger_user_json['is_active'] = ledger_obj.is_active
            ledger_user_json['date_joined'] = ledger_obj.date_joined.strftime('%d/%m/%Y %H:%M')
            ledger_user_json['title'] = ledger_obj.title
            ledger_user_json['dob'] = ledger_obj.dob.strftime('%d/%m/%Y %H:%M')
            ledger_user_json['phone_number'] = ledger_obj.phone_number
            ledger_user_json['position_title'] = ledger_obj.position_title
            ledger_user_json['mobile_number'] = ledger_obj.mobile_number
            ledger_user_json['fax_number'] = ledger_obj.fax_number
            ledger_user_json['organisation'] = ledger_obj.organisation
            #ledger_user_json['residential_address'] = ledger_obj.residential_address
            #ledger_user_json['postal_address'] = ledger_obj.postal_address
            #ledger_user_json['billing_address'] = ledger_obj.billing_address
            ledger_user_json['identification'] = ledger_obj.identification
            ledger_user_json['senior_card'] = ledger_obj.senior_card
            ledger_user_json['character_flagged'] = ledger_obj.character_flagged
            ledger_user_json['character_comments'] = ledger_obj.character_comments
            ledger_user_json['extra_data'] = ledger_obj.extra_data
            
            ledger_user_json['fullname'] = ledger_obj.get_full_name()
            ledger_user_json['fullnamedob'] = ledger_obj.get_full_name_dob()
 
    jsondata['user'] = ledger_user_json





























          


    return HttpResponse(json.dumps(jsondata), content_type='application/json')