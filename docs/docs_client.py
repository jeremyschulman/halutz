from halutz.client import Client
import json

base_url = 'http://localhost:32768'
swagger_spec = json.load(open('swagger_spec.json'))

client = Client(base_url=base_url, spec_dict=swagger_spec)
