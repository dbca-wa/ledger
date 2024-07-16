import traceback
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from rest_framework import viewsets, serializers, status, generics, views
from ledger.accounts import helpers
from ledger.accounts.reports import user_report
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication, BasicAuthentication 
from ledger.accounts import models as accounts_models
from django.db.models import Q
import json


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

class UserReportView(views.APIView):

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            report = None
            if helpers.is_account_admin(self.request.user) is True:
                filename = 'duplicate-identity-report'
                # Generate Report
                report = user_report()
                if report:
                    response = HttpResponse(FileWrapper(report), content_type='text/csv')
                    response['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
                    return response
                else:
                    raise serializers.ValidationError('No report was generated.')
            else:
                 raise serializers.ValidationError('Access Forbidden')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))
        

class UserAccountsList(views.APIView):
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    def enforce_csrf(self, *args, **kwargs):
        '''
        Bypass the CSRF checks altogether
        '''
        pass    
    # def get(self,request,format=None):
    #     try:
    #         http_status = status.HTTP_200_OK
    #         report = None
    #         if helpers.is_account_admin(self.request.user) is True:
    #             # request_body_json = json.loads(request.body.decode("utf-8"))
    #             # print (request_body_json)
    #             draw  = int(request.GET.get('draw', 10))
    #             page_length  = int(request.GET.get('length', 10))
    #             # page_length = request_body_json['length'] 
    #             # request.POST.get('length', 10)
    #             row_start  = int(request.GET.get('start', 0))
    #             search_value  = request.GET.get('search[value]', '')
                
    #             # row_start = request_body_json['start']
    #             active = True
    #             # if "active" in request_body_json:
    #             #     active = request_body_json['active']
    #             # search_value = request_body_json['search']['value']

    #             #request.POST.get('start', 0)
    #             print (page_length)
    #             print (row_start)
               
    #             print ("SEARCH")
    #             print (search_value)
    #             query = Q()
    #             query &= Q(is_active=active)
    #             if search_value:
    #                 if len(search_value) > 0:
    #                     query &= Q(
    #                         Q(first_name__icontains=search_value) | Q(last_name__icontains=search_value)
    #                     )

    #             accounts_array= []
    #             accounts_total = accounts_models.EmailUser.objects.all().count()                
    #             accounts_filtered = accounts_models.EmailUser.objects.filter(query).count() 
    #             accounts_obj = accounts_models.EmailUser.objects.filter(query)[row_start:page_length]

    #             print ("ACCOUNT TOTAL")
    #             print (accounts_total)
    #             for acc in accounts_obj:
    #                 account_row = {}
    #                 account_row["id"] = acc.id
    #                 account_row["account_first_name"] = acc.first_name
    #                 # account_row["account_last_name"] = acc.last_name
    #                 # account_row["legal_first_name"] = "" #acc.legal_first_name
    #                 # account_row["legal_last_name"] = "" #acc.legal_last_name
    #                 # if acc.dob:
    #                 #     account_row["account_dob"] = acc.dob.strftime("DD/MM/YYY")
    #                 # else:
    #                 #     account_row["account_dob"] = ""
    #                 # if acc.legal_dob:
    #                 #     account_row["legal_dob"] = acc.legal_dob.strftime("DD/MM/YYY")
    #                 # else:
    #                 #      account_row["legal_dob"] = ""
    #                 # account_row["email"] = acc.email
    #                 # account_row["action"] = ''
    #                 accounts_array.append(account_row)



    #             # Generate Users
    #             dt_obj = {  "draw": draw,
    #                         "recordsTotal": accounts_total,
    #                         "recordsFiltered": accounts_filtered,                    
    #                         "data" : accounts_array
    #                     }
                
    

                
    #             if dt_obj:
    #                 response = HttpResponse(json.dumps(dt_obj), content_type='application/json')
    #                 return response
    #             else:
    #                 raise serializers.ValidationError('No report was generated.')
    #         else:
    #              raise serializers.ValidationError('Access Forbidden')
    #     except serializers.ValidationError:
    #         raise
    #     except Exception as e:
    #         traceback.print_exc()
    #         raise serializers.ValidationError(str(e))        

    def clean_string(self,value):
        if value is None:
            value = ""
        return value
    def post(self,request,format=None):
  
    
        try:
            http_status = status.HTTP_200_OK
            report = None
            if helpers.is_account_admin(self.request.user) is True:
                request_body_json = json.loads(request.body.decode("utf-8"))                
                page_length = request_body_json['length']                 
                row_start = request_body_json['start']
                draw = request_body_json['draw']
                order_column_id = ''
                order_direction = ''
                if len(request_body_json['order']) > 0:
                    order_column_id = request_body_json['order'][0]['column']
                    order_direction = request_body_json['order'][0]['dir']

                order_dir = ""
                if order_direction == 'desc':
                    order_dir= "-"

                order_by = ["id",]
                if order_column_id == 0:
                    order_by = [order_dir+'id',]
                if order_column_id == 1:
                    order_by = [order_dir+'first_name', order_dir+'last_name']
                if order_column_id == 2:
                    order_by = [order_dir+'legal_first_name', order_dir+'legal_last_name']
                if order_column_id == 3:
                    order_by = [order_dir+'dob',]                  
                if order_column_id == 4:
                    order_by = [order_dir+'legal_dob',]                                        
                if order_column_id == 5:
                    order_by = [order_dir+'email',]

                active = True
                if "active" in request_body_json:
                    active = request_body_json['active']
                search_value = request_body_json['search']['value']

                query = Q()
                query &= Q(is_active=active)
                
                if search_value:
                    if len(search_value) > 0:
                        if search_value.isnumeric() is True:
                            query &= Q(            
                                Q(id=search_value)
                                | Q(phone_number__icontains=search_value)
                                | Q(mobile_number__icontains=search_value)
                            )
                        else:
                            query &= Q(
                                Q(first_name__icontains=search_value) 
                                | Q(last_name__icontains=search_value)
                                | Q(legal_first_name__icontains=search_value)
                                | Q(legal_last_name__icontains=search_value)
                                | Q(email__icontains=search_value)
                          

                            )

                accounts_array= []
                accounts_total = accounts_models.EmailUser.objects.all().count()                
                accounts_filtered = accounts_models.EmailUser.objects.filter(query).count() 
                accounts_obj = accounts_models.EmailUser.objects.filter(query).order_by(*order_by)[row_start:row_start+page_length]

                for acc in accounts_obj:
                    account_row = {}
                    account_row["id"] = acc.id
                    account_row["account_name"] = self.clean_string(acc.first_name) +' '+ self.clean_string(acc.last_name)
                    
                    account_row["legal_name"] = self.clean_string(acc.legal_first_name) + ' '+self.clean_string(acc.legal_last_name)
              
                    if acc.dob:
                        account_row["account_dob"] = acc.dob.strftime("%d/%m/%Y")
                    else:
                        account_row["account_dob"] = ""
                    if acc.legal_dob:
                        account_row["legal_dob"] = acc.legal_dob.strftime("%d/%m/%Y")
                    else:
                         account_row["legal_dob"] = ""
                    account_row["email"] = acc.email
                    account_row["action"] = "<a class='btn btn-primary btn-sm' href='/ledger/account-management/"+str(acc.id)+"/change/'>Change</a>"
                    accounts_array.append(account_row)
                


                # Generate Users
                dt_obj = {  "draw": draw,
                            "recordsTotal": accounts_total,
                            "recordsFiltered": accounts_filtered,                    
                            "data" : accounts_array
                        }
                
                
                
                if dt_obj:
                    response = HttpResponse(json.dumps(dt_obj), content_type='application/json')
                    return response
                else:
                    raise serializers.ValidationError('No report was generated.')
            else:
                 raise serializers.ValidationError('Access Forbidden')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))        
        


class UserAccountsLogsList(views.APIView):
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    def enforce_csrf(self, *args, **kwargs):
        '''
        Bypass the CSRF checks altogether
        '''
        pass

    def clean_string(self,value):
        if value is None:
            value = ""
        return value                
    def post(self,request,pk, format=None):
        try:
            http_status = status.HTTP_200_OK
            report = None
            if helpers.is_account_admin(self.request.user) is True:                
                request_body_json = json.loads(request.body.decode("utf-8"))
                
                page_length = request_body_json['length']                 
                row_start = request_body_json['start']
                draw = request_body_json['draw']       

                order_column_id = ''
                order_direction = ''
                if len(request_body_json['order']) > 0:
                    order_column_id = request_body_json['order'][0]['column']
                    order_direction = request_body_json['order'][0]['dir']   

                order_dir = ""
                if order_direction == 'desc':
                    order_dir= "-"

                query = Q()
                order_by = ["id",]
                if order_column_id == 0:
                    order_by = [order_dir+'id',]
                if order_column_id == 1:
                    order_by = [order_dir+'change_key',]
                if order_column_id == 2:
                    order_by = [order_dir+'change_value',]
                if order_column_id == 3:
                    order_by = [order_dir+'change_by',]   
                if order_column_id == 4:
                    order_by = [order_dir+'created',]                    


                search_value = request_body_json['search']['value']

                query = Q(emailuser_id=pk)            
                if search_value:
                    if len(search_value) > 0:
                        if search_value.isnumeric() is True:
                            query &= Q(            
                                Q(id=search_value)
                            )
                        else:
                            query &= Q(
                                Q(change_key__icontains=search_value) 
                                | Q(change_value__icontains=search_value)                                                          
                            )


                accounts_log_array= []
                accounts_log_total = accounts_models.EmailUserChangeLog.objects.all().count()                
                accounts_log_filtered = accounts_models.EmailUserChangeLog.objects.filter(query).count() 
                accounts_log_obj = accounts_models.EmailUserChangeLog.objects.filter(query).order_by(*order_by)[row_start:row_start+page_length]
                for acc in accounts_log_obj:
                    account_log_row = {}
                    account_log_row["id"] = acc.id
                    account_log_row["emailuser"] = self.clean_string(acc.emailuser.first_name) +' '+ self.clean_string(acc.emailuser.last_name)
                    account_log_row["change_key"] = acc.change_key
                    account_log_row["change_value"] = acc.change_value
                    if acc.change_by:
                        account_log_row["change_by"] = self.clean_string(acc.change_by.first_name) +' '+ self.clean_string(acc.change_by.last_name) + ' ({})'.format(acc.change_by.id)
                    else:
                        account_log_row["change_by"] = ''
                    account_log_row["created"]  = acc.created.astimezone().strftime("%d %b %Y %H:%M %p")
                    accounts_log_array.append(account_log_row)

                # Generate Users
                dt_obj = {  "draw": draw,
                            "recordsTotal": accounts_log_total,
                            "recordsFiltered": accounts_log_filtered,                    
                            "data" : accounts_log_array
                        }
                
                if dt_obj:
                    response = HttpResponse(json.dumps(dt_obj), content_type='application/json')
                    return response
                else:
                    raise serializers.ValidationError('No data was generated.')                
            else:
                raise serializers.ValidationError('Access Forbidden')                                    

        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))                                                    