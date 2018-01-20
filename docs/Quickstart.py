
# coding: utf-8

# Create a client for system that uses a Token in the request header.  We create a requests Session instance and pass this to `halutlz` when creating the client.

# In[1]:


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

# In[ ]:


resp, ok = client.request.ipam.ipam_vlans_list(name="Blue")


# In[ ]:


vlan_data = resp['results'][0]


# In[ ]:


print "VLAN-ID is: %s " % vlan_data['vid']


# Now change the VLAN-ID value to 1001

# In[ ]:


rqst = client.request.ipam.ipam_vlans_partial_update
rqst.data.vid = 1001


# In[ ]:


rqst.data.validate()


# In[ ]:


resp, ok = rqst(id=vlan_data['id'])


# In[ ]:


ok


# In[ ]:


resp, ok = client.request.ipam.ipam_vlans_read(id=vlan_data['id'])


# In[ ]:


ok


# In[ ]:


resp

