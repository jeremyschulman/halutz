# halutz

Halutz is a python library for working with an [Swagger](https://swagger.io/) based systems.


It is built around [bravado](https://github.com/Yelp/bravado) and
 [python-jsonschema-objects](https://github.com/cwacek/python-jsonschema-objects)


# Quickstart

````python
from halutz.client import Client
from requests.sessions import Session

my_session = Session()
my_session.headers['Authorization'] = "Token My-Token-Value"
my_api_url = 'http://localhost:32768'
my_api_doc_url = my_api_url + "/api/docs?format=openapi"

client = Client(origin_url=my_api_url, 
                spec_dict=my_session.get(my_api_doc_url).json(),
                requests_session=my_session)
    

# Given an API Swagger spec that has an API with a tag='design'
# and an operationID='get_rack_types', get a Request instance.

rqst = client.request.design.get_rack_types

# This request has no parameters, but if it did you would
# pass them as key-value pairs when you execute the request.  When
# you execute the request, will get back a tuple that is  
# the response data, and ok=True/False if the command
# was successful.

respose, ok = rqst()

if not ok:
    raise RuntimeError(
    'cannot run command, debug this response: ', response)

# Or you might want to get a specific command if you know the API
# path

rqst = client.command_request('get', '/api/design/rack-types')

# Or you might want to get the collection of all commands
# for a givent path.  For example, let's say the
# given path supports both a 'get' and a 'post' command:

rack_api = client.path_requests('/api/design/rack-types')

get_racks = rack_api.get
create_rack = rack_api.post

# Of course, you could simply execute the command without keeping
# the request instance, like this:

got_racks, ok = rack_api.get()

# Finally, there is a simple integration with the python-jsonschema-objects
# metabuild sysetm so that you can create request body payloads and validate
# the data before sending the command.  That tutorial will be provided soon.
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
