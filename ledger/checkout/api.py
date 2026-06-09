from django.urls import reverse
from rest_framework import views
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets, serializers, status, generics, views
from django.http import HttpResponse, HttpResponseRedirect

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
    


class PaymentCompletionWehook(views.APIView):
    renderer_classes = (JSONRenderer,)
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            print (request.POST)                 
            print (request.GET)  
            return HttpResponse(json.dumps({'status': 200, 'message': 'success'}), content_type='application/json')         
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))
        
    def post(self, request, *args, **kwargs):
        print ("TEST JM")
        # print (request.POST)                 
        # print (request.GET)         

        try:

            if hasattr(request, '_body'):
                raw_data = request._body
            else:
                raw_data = request.body
                print (raw_data)

            # 1. Parse the JSON payload from the request body
            payload = json.loads(request.body.decode('utf-8'))

            receipt_number = payload['data'].get('receiptNumber')
            response_code = payload['data'].get('ResponseCode')   # "0" typically indicates a success state
            response_text = payload['data'].get('ResponseText')
            amount_in_cents = payload['data'].get('Amount')  
            print("START")
            print (receipt_number)

            print (payload)
        except Exception as e:
            print ("ERROR")
            print (e)
            # return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)

        return Response({"message": "CSRF check bypassed!"})