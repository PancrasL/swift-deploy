import zlib
import requests
def hello(event, context):
    req = event['extensions']['request']
    ndp_type = req.forms.get('ndp_type')
    obj_url = req.forms.get('proxy_link')

    data = None
    if(ndp_type == 'GET'):
        data = requests.get(obj_url).content
    else:
        data = event['data']
    data = process(data)
    if(ndp_type == 'PUT'):
        return requests.put(obj_url,data)
    return data

def process(data):
    return zlib.compress(data)