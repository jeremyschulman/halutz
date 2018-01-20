# halutz

Halutz is a python library for working with an [Swagger](https://swagger.io/) based systems.


It is built around [bravado](https://github.com/Yelp/bravado) and
 [python-jsonschema-objects](https://github.com/cwacek/python-jsonschema-objects)


````python

# Create a client for system that uses a Token in the request header.  We create a requests Session instance and pass this to `halutlz` when creating the client.

# In[29]:


from halutz.client import Client
from requests.sessions import Session

my_session = Session()
my_session.headers['Authorization'] = "Token 0123456789abcdef0123456789abcdef01234567"
my_api_url = 'http://localhost:32768'
my_api_doc_url = my_api_url + "/api/docs?format=openapi"

client = Client(origin_url=my_api_url, 
                spec_dict=my_session.get(my_api_doc_url).json(),
                requests_session=my_session)


# Create a request for updating an existing VLAN, let's presume prima

# In[30]:


resp, ok = client.request.ipam.ipam_vlans_list(name="Blue")


# In[31]:


vlan_data = resp['results'][0]


# In[32]:


print "VLAN-ID is: %s " % vlan_data['vid']


# Now change the VLAN-ID value to 1001

# In[33]:


rqst = client.request.ipam.ipam_vlans_partial_update
rqst.data.vid = 1001


# In[34]:


rqst.data.validate()


# In[35]:


resp, ok = rqst(id=vlan_data['id'])


# In[36]:


ok


# In[37]:


resp, ok = client.request.ipam.ipam_vlans_read(id=vlan_data['id'])


# In[38]:


ok


# In[39]:


resp


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
