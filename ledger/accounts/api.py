import traceback
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from rest_framework import viewsets, serializers, status, generics, views

from ledger.accounts.reports import user_report

class UserReportView(views.APIView):

    def get(self,request,format=None):
        try:
            http_status = status.HTTP_200_OK
            report = None

            filename = 'duplicate-identity-report'
            # Generate Report
            report = user_report()
            if report:
                response = HttpResponse(FileWrapper(report), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
                return response
            else:
                raise serializers.ValidationError('No report was generated.')
        except serializers.ValidationError:
            raise
        except Exception as e:
            traceback.print_exc()
            raise serializers.ValidationError(str(e))