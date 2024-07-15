from __future__ import unicode_literals
import json

def Validation(checkname, context):
    if checkname == "referrals":
        donothing  = "more to come just added as a place holder"


def Attachment_Extension_Check(attach_list_type,attachments,allow_extension_types): 
    """ Purpose is to allow file extension to be checked and only allow extensions that are allowed
    """

    allowed = False 

    if allow_extension_types is None:
        allow_extension_types = ['.pdf','.xls','.doc','.jpg','.png','.xlsx','.docx']

    if attach_list_type == 'multi':
        """ Check a list for any attachment not meeting the allow extension list.
        """
        allowed = True
        for fi in attachments:
            extension = fi.name.split('.')

            att_ext = str("."+extension[1]).lower()
            if att_ext not in allow_extension_types:
                allowed = False

    else:
        """ By Default Assume only a single attachment
        """
        extension = attachments.name.split('.')
        att_ext = str("."+extension[1]).lower()
        if att_ext in allow_extension_types:
            allowed = True

    return allowed

def is_json(myjson):
  try:
    json_object = json.loads(myjson)
  #except ValueError, e:
  except ValueError:
    return False
  return True