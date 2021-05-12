import requests
import base64 
import mimetypes
import json

# configs
api_key='QYJVB595A6VLM4O50L9KMD7GXET2FS3IOP1WW30KBFI8K50KEPA56H08VYTU4SV0BWD4GLU6MPYGS9MBRZQWV70Y46XZUQUW2K8Y'
url = 'http://172.17.0.3:9002/ledgergw/remote/documents/get/'+api_key+'/'
myobj = {'private_document_id': 15}
# send request to server to get file
resp = requests.post(url, data = myobj)
filename = resp.json()['filename']
extension = resp.json()['extension']
# base64data
print (resp.json()['data'])
image_64_decode = base64.b64decode(resp.json()['data'])
image_result = open(filename+'.'+extension, 'wb') # create a writable image and write the decoding result
image_result.write(image_64_decode)
#print (resp.text)

