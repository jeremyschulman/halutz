
Create a client for system that uses a Token in the request header.  We create a requests Session instance and pass this to `halutlz` when creating the client.


```python
from halutz.client import Client
from requests.sessions import Session

my_session = Session()
my_session.headers['Authorization'] = "Token 0123456789abcdef0123456789abcdef01234567"
my_api_url = 'http://localhost:32768'
my_api_doc_url = my_api_url + "/api/docs?format=openapi"

client = Client(origin_url=my_api_url, 
                spec_dict=my_session.get(my_api_doc_url).json(),
                requests_session=my_session)
```

Create a request for updating an existing VLAN, let's presume prima


```python
resp, ok = client.request.ipam.ipam_vlans_list(name="Blue")
```


```python
vlan_data = resp['results'][0]
```


```python
print "VLAN-ID is: %s " % vlan_data['vid']
```

    VLAN-ID is: 1001 


Now change the VLAN-ID value to 1001


```python
rqst = client.request.ipam.ipam_vlans_partial_update
rqst.data.vid = 1001
```


```python
rqst.data.validate()
```




    True




```python
resp, ok = rqst(id=vlan_data['id'])
```


```python
ok
```




    True




```python
resp, ok = client.request.ipam.ipam_vlans_read(id=vlan_data['id'])
```


```python
ok
```




    True




```python
resp
```




    {u'custom_fields': {},
     u'description': u'',
     u'display_name': u'1001 (Blue)',
     u'group': None,
     u'id': 1,
     u'name': u'Blue',
     u'role': None,
     u'site': None,
     u'status': {u'label': u'Active', u'value': 1},
     u'tenant': None,
     u'vid': 1001}


