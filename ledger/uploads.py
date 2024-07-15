from django.http import HttpResponse
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.conf import settings
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser
from confy import env
from ledger.accounts.models import PrivateDocument
import json
from django.utils.safestring import SafeText
from ledger.validationchecks import Attachment_Extension_Check, is_json
"""
This is a upload wrapper for the ajax uploader widget for django forms.
"""

def PrivateMediaUploads(request):
    #  print request.FILES
    file_group = request.POST.get('file_group',None)
    file_group_ref_id = request.POST.get('file_group_ref_id',None)

    object_hash = {'status':'success','message':''} 
    allow_extension_types = ['.pdf','.xls','.doc','.jpg','.png','.xlsx','.docx','.msg','.txt']

    for f in request.FILES.getlist('files'):
         extension = f.name.split('.')
         att_ext = str("."+extension[1]).lower()
         if att_ext not in allow_extension_types:
             object_hash['status'] = 'error'
             object_hash['message'] = 'Extension not allowed'+str(att_ext)
                 
             json_hash = json.dumps(object_hash)
             return HttpResponse(json_hash, content_type='text/html')

    #for f in request.FILES.getlist('__files[]'):
         doc = PrivateDocument()
         doc.upload = f
         doc.name = f.name
         doc.file_group = int(file_group)
         doc.file_group_ref_id =int(file_group_ref_id)
         doc.extension = att_ext
         doc.save()
#         self.object.records.add(doc)
#         print doc.id
         object_hash['doc_id'] = doc.id
         object_hash['path'] = doc.upload.name
         object_hash['url_parth'] = 'private-media/view/'+str(doc.id)+'-file'+att_ext
         object_hash['short_name'] = SafeText(doc.upload.name)[19:]
         object_hash['name'] = doc.name
         object_hash['file_group'] = doc.file_group       
         object_hash['file_group_ref_id'] = doc.file_group_ref_id
         object_hash['extension'] = doc.extension

         doc2 = PrivateDocument.objects.get(id=object_hash['doc_id'])
         # print doc
    json_hash = json.dumps(object_hash)
    return HttpResponse(json_hash, content_type='text/html')