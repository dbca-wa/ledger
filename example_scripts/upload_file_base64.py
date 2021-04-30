import requests
import base64 
import mimetypes

filename="./base64file.pdf"
api_key='QYJVB595A6VLM4O50L9KMD7GXET2FS3IOP1WW30KBFI8K50KEPA56H08VYTU4SV0BWD4GLU6MPYGS9MBRZQWV70Y46XZUQUW2K8Y'
url = 'http://172.17.0.3:9002/ledgergw/remote/documents/update/'+api_key+'/'

text_file = open(filename, "r")
data = text_file.read()
text_file.close()

extension =''
if filename[-4:][:-3] == '.':
    extension = filename[-3:]
if filename[-5:][:-4] == '.':
    extension = filename[-4:]
print (filename[-4:][:-3])
print (filename[-5:][:-4])

#if filename[-4][-3] ==
#print (data:text/plain;base64,
#print (mimetypes.types_map['.'+str(extension)])
#base64file  (base64.b64decode(data))

base64_url = "data:"+mimetypes.types_map['.'+str(extension)]+";base64,"+data
myobj = {'emailuser_id' : 7,'filebase64': base64_url, 'extension': extension, 'file_group_id': 1}
resp = requests.post(url, data = myobj)
print (resp.text)

# 
#print (resp.text)


