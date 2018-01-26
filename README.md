# Halutz

Halutz is a python library for working with systems using [Swagger](https://swagger.io/), a popular way to define 
and interact with RESTful APIs. The purpose of a halutz client is to:

   * Account for systems that require any form of API authentication
   * Provide *user-friedly* access to all API request commands
   * Provide for the interactive instrospection of API capabilities
   * Create python objects required by request body-parameters
   * Perform data validation using the Swagger spec

Halutz was inspired by working with network engineers that are getting started with Python.  
Network engineers are masters of complex CLIs.  Network engineers can use haltuz based clients 
with [IPython](https://ipython.org/) and Juptyer notebooks to *interactively* automate systems *CLI-like* manner. 

*click on video to see larger format*

<a href="https://vimeo.com/251980848"><img src="docs/media/halutz-splashpage.gif" title="halutz"/></a>
     
# Installation

````bash
pip install halutz
````

# Documentation

Tutorials in the form of jupyter notebooks are located in the [docs](docs/README.md) directory.

# Quickstart

Create a client for system that uses a Token in the request header.
We create a `requests.Session` instance, setup the header, and pass this to halutz 
when creating the client.

For this exmaple, we are working with Netbox, and we will change the VLAN
named "Blue" to have a VLAN-ID = 1001.

```python
from halutz.client import Client
from requests.sessions import Session
import json

my_session = Session()
my_session.headers['Authorization'] = "Token 0123456789abcdef0123456789abcdef01234567"
my_api_url = 'http://localhost:32768'
my_api_doc_url = my_api_url + "/api/docs?format=openapi"

client = Client(server_url=my_api_url, 
                origin_spec=my_session.get(my_api_doc_url).json(),
                session=my_session)

# retrieve the VLAN with name "Blue".  When executing a request
# we get back a tuple of (response, ok_fail).  We need to get
# the vlan data so we have the ID value when we do the update.

resp, ok = client.request.ipam.ipam_vlans_list(name="Blue")
vlan_data = resp['results'][0]

# Create the request to update the VLAN.  As part of getting the request, the request 
# will include an instance of the body parameter.  You can set these, 
# and they are validated as you do.  Additionally we can ensure we've filled out 
# the edit_vlan.data properly by using the validate method.

edit_vlan = client.request.ipam.ipam_vlans_partial_update
edit_vlan.data.vid = 1001
edit_vlan.data.validate()

# now execute the request to edit the VLAN, by calling it, and passing in the 
# required parameters as arguments; in this case, just the `id` parameter.  You do not need to
# explicity pass the `data` body parameter as part of the call arguments.

resp, ok = edit_vlan(id=vlan_data['id'])

print json.dumps(resp, indent=2)
```

outputs:
```text
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
```


# Questions?

If you have questions, or would like to request additional tutorials, features, etc.
please open an issue.
