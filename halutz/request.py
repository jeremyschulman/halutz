import six
from first import first
import json

import msgpack
from bravado_core.content_type import APP_JSON, APP_MSGPACK
import bravado.exception

__all__ = ['Request']


class Request(object):

    def __init__(self, client, command):
        self.client = client

        # see if there is an 'in body' parameter

        self.body_param = first(
            p_name for p_name, p_obj in six.iteritems(command.params)
            if p_obj.param_spec['in'] == 'body')

        self.command = command
        self.command.also_return_response = True
        self.operation = command.operation
        self.model_response = client.model_response or False

        # automatically create an instance of the body class if there
        # is one in the command spec.  attach the attribute as the
        # body parameter name.

        if self.body_param:
            body_inst = client.build.body_class(command.params[self.body_param])()
            setattr(self, self.body_param, body_inst)

    @property
    def path(self):
        return self.operation.path_name

    @property
    def method(self):
        return self.operation.http_method

    @property
    def spec(self):
        return self.operation.op_spec

    @property
    def params(self):
        return self.command.operation.params

    @staticmethod
    def _unmarshal_response(response):
        content_type = response.headers.get('content-type', '').lower()

        if content_type.startswith(APP_JSON) or content_type.startswith(APP_MSGPACK):
            # content_spec = deref(response_spec['schema'])
            if content_type.startswith(APP_JSON):
                content_value = response.json()
            else:
                content_value = msgpack.loads(response.raw_bytes, encoding='utf-8')

            return content_value
        elif content_type.startswith('text'):
            return response.text

        return None

    def __call__(self, **params):
        """ execute the request and return the (response, ok) tuple """

        # auto-add body if exists and not provided by caller.
        if self.body_param and self.body_param not in params:
            body_attr = getattr(self, self.body_param)
            params[self.body_param] = (
                body_attr.for_json() if hasattr(body_attr, 'for_json')
                else body_attr)

        try:

            rqst = self.command(**params)
            resp_data, http_resp = rqst.result()

            # if there is no resp_data, it means that there is no response-schema
            # defined, and the bravado library doesn't return anything.  therefore
            # we need to unmarshal the data here.

            if resp_data is None:
                resp_data = self._unmarshal_response(http_resp)

            if self.model_response:
                # if the caller wants the response data returned as a schema-object,
                # then first get the class; and if one exists, then use the http response
                # data to create the model object.

                resp_cls = self.client.build.resp_class(
                    request=self, status_code=http_resp.status_code)

                if resp_cls:
                    resp_data = resp_cls(**resp_data)

            return resp_data, True

        except bravado.exception.HTTPClientError as exc:
            http_resp = exc.response
            return (http_resp, str(http_resp), http_resp.text), False

    def __repr__(self):
        return "Request: %s" % json.dumps({
            'method': self.method,
            'path': self.path,
            'params': self.params.keys()
        }, indent=3)
