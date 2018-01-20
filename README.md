# halutz

Halutz is a python library for working with an [Swagger](https://swagger.io/) based systems.

It is built around [bravado](https://github.com/Yelp/bravado) and
 [python-jsonschema-objects](https://github.com/cwacek/python-jsonschema-objects)

# Quick Start

Create a client for system that uses a Token in the request header. We create a requests Session instance
and pass this to halutlz when creating the client.


```python
from halutz.client import Client
from requests.sessions import Session
import json

my_session = Session()
my_session.headers['Authorization'] = "Token 0123456789abcdef0123456789abcdef01234567"
my_api_url = 'http://localhost:32768'
my_api_doc_url = my_api_url + "/api/docs?format=openapi"

client = Client(origin_url=my_api_url, 
                spec_dict=my_session.get(my_api_doc_url).json(),
                requests_session=my_session)

resp, ok = client.request.ipam.ipam_vlans_list(name="Blue")

vlan_data = resp['results'][0]

print "VLAN-ID is: %s " % vlan_data['vid']
```
outputs:
```text
VLAN-ID is: 12 
```
Create a request to change the VID

```python
edit_vlan = client.request.ipam.ipam_vlans_partial_update
edit_vlan.data.vid = 1001

# check for valid data, if not valid, this will raise an Exception
edit_vlan.data.validate()

# now execute the edit on the VLAN, 
resp, ok = edit_vlan(id=vlan_data['id'])

print json.dumps(resp, indent=2)
```
````text
    {
      "status": 1, 
      "group": null, 
      "name": "Blue", 
      "vid": 1001, 
      "site": null, 
      "role": null, 
      "custom_fields": {}, 
      "id": 1, 
      "tenant": null, 
      "description": ""
    }
````



# Why Another Swagger Client library?

OpenAPI (fka Swagger) is a popular way to define and interact with RESTful systems. I work with
network engineers that are getting started with Python.  Network engineers are masters of
complex CLIs.  I've started using [ipython](https://ipython.org/) and Juptyer notebooks
as a way to *interactively* use Python to automate systems -- and this gives the user
as CLI look-and-feel.  I wanted to create a library that would allow them to *interactively*  
work with OpenAPI based system.  To do this, I combined the 
 client library with the  library in a way that provides
a very friendly and feature rich way to interact with these systems.  I will be creating a number of
tutorials using Jupyter notebooks to showcase these feature.  For now, here is a Quickstart  


# Stay Tuned for more Tutorials!

Cheers,
<br>
-- Jeremy Schulman, [@nwkautomaniac](https://twitter.com/nwkautomaniac)
<br>
Developer Advocate at [Apstra, Inc.](www.apstra.com)
