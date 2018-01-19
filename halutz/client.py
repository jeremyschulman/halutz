
import six
from first import first
from copy import deepcopy
import json

from jsonschema.compat import lru_cache

# from the python-jsonschema-objects package

from python_jsonschema_objects import ObjectBuilder
from python_jsonschema_objects.classbuilder import ClassBuilder

# from the bravado packages
import msgpack
from bravado_core.spec import Spec
from bravado_core. resource import Resource as BravadoResource
from bravado_core.content_type import APP_JSON, APP_MSGPACK
from bravado.client import CallableOperation, ResourceDecorator
from bravado.requests_client import RequestsClient
import bravado.exception


__all__ = ['Client']


class Client(object):

    def __init__(self, origin_url, spec_dict,
                 requests_session=None, remote=None):

        self.origin_url = origin_url
        self.origin_spec = deepcopy(spec_dict)
        self.requests_session = requests_session
        self.remote = remote

        # bravado swagger spec created from the origin_spec, linking
        # the bravado requests session to the AOSpy session

        self.swagger_spec = self.make_swagger_spec()

        # alias for ease-of-use
        self.definitions = self.origin_spec.get('definitions') or {}

        # function to de-reference '$ref' items
        self.deref = self.swagger_spec.deref

        # control if the request response content should be automatically
        # be returned as a modeled object (using the associated schema def)
        # or as-is content from the AOS.  By default set this to as-is.
        # caller can set this to True so that all responses are handled
        # the same; or they can set this on a request-by-request bases
        # in the Request instance.

        self.model_response = False

        # setup request methods to create Request instances for command
        # execution.

        rqst_factory = RequestFactory(self)
        self.request = rqst_factory.attr_factory()
        self.command_request = rqst_factory.command_request
        self.path_requests = rqst_factory.path_requests

        # object to use for building jsonschema classes/instances
        self.build = SchemaObjectFactory(self)

    def make_swagger_spec(self):
        http_client = RequestsClient()

        # if the caller provided an existing requests session,
        # then use there here.

        if self.requests_session:
            http_client.session = self.requests_session

        return Spec.from_dict(
            spec_dict=self.origin_spec,
            origin_url=self.origin_url,
            http_client=http_client,

            # TODO expose these configuration options to the
            # TODO caller; hardcoded for now.  caller could make
            # TODO updates to the self.swagger_spec value

            config={
                'validate_swagger_spec': False,
                'validate_responses': False,
                'use_models': False
            }
        )

    def __repr__(self):
        return json.dumps({
            'client-url': self.origin_url
        })


class SchemaObjectFactory(object):

    def __init__(self, client):
        self.deref = client.deref
        self.definitions = client.definitions
        self._model_cache = lru_cache()(self.__model_class)

    @staticmethod
    def schema_model_name(object_schema):
        return first(map(object_schema.get,
                         ['x-model', 'title', 'id']))

    @staticmethod
    def schema_class(object_schema, model_name, classes=False):
        """
        Create a object-class based on the object_schema.  Use
        this class to create specific instances, and validate the
        data values.  See the "python-jsonschema-objects" package
        for details on further usage.

        Parameters
        ----------
        object_schema : dict
            The JSON-schema that defines the object

        model_name : str
            if provided, the name given to the new class.  if not
            provided, then the name will be determined by
            one of the following schema values, in this order:
            ['x-model', 'title', 'id']

        classes : bool
            When `True`, this method will return the complete
            dictionary of all resolved object-classes built
            from the object_schema.  This can be helpful
            when a deeply nested object_schema is provided; but
            generally not necessary.  You can then create
            a :class:`Namespace` instance using this dict.  See
            the 'python-jschonschema-objects.utls' package
            for further details.

            When `False` (default), return only the object-class

        Returns
        -------
            - new class for given object_schema (default)
            - dict of all classes when :param:`classes` is True
        """

        # if not model_name:
        #     model_name = SchemaObjectFactory.schema_model_name(object_schema)

        obj_bldr = ObjectBuilder(object_schema)
        cls_bldr = ClassBuilder(obj_bldr.resolver)
        model_cls = cls_bldr.construct(model_name, object_schema)

        # if `classes` is False(0) return the new model class,
        # else return all the classes resolved

        return [model_cls, cls_bldr.resolved][classes]

    def __model_class(self, model_name):
        """ this method is used by the lru_cache, do not call directly """
        build_schema = deepcopy(self.definitions[model_name])
        return self.schema_class(build_schema, model_name)

    def model_class(self, model_name):
        return self._model_cache(model_name)

    # -------------------------------------------------------------------------
    # for use by the Request class to create instances of the body and
    # and response json-dict data
    # -------------------------------------------------------------------------

    def body_class(self, body_param):
        body_schema = self.deref(body_param.param_spec['schema'])

        cache_name = (self.schema_model_name(body_schema) or
                      str(id(body_schema)))

        if cache_name not in self.definitions:
            self.definitions[cache_name] = body_schema

        return self._model_cache(cache_name)

    def resp_class(self, request, status_code):
        resp_schema = self.deref(request.spec['responses'][str(status_code)]['schema'])
        return (None if not resp_schema
                else self._model_cache(resp_schema['x-model']))


class RequestFactory(object):

    class Resource(object):
        """ wrapper around the bravado ResourceDecorator to facilite this factory """
        def __init__(self, client, resource):
            self._client = client
            self._resource = resource

        def __getattr__(self, item):
            return Request(self._client,
                           getattr(self._resource, item))

        def __dir__(self):
            return self._resource.__dir__()

    class ViaAttr(object):
        def __init__(self, factory):
            self._factory = factory

        def __getattr__(self, attr):
            """
            Returns a single Request instance for a give command.  For example:

                >>> client = Client()
                >>> rqst = client.request.hcl.get_api_hcl
                >>> resp, ok = rqst()

            """
            return RequestFactory.Resource(
                self._factory.client,
                ResourceDecorator(self._factory.resources[attr]))

        def __dir__(self):
            return self._factory.resources.keys()

    def __init__(self, client):
        """ client is an OpenApiClient instance """
        self.client = client
        self.resources = client.swagger_spec.resources

    def attr_factory(self):
        return RequestFactory.ViaAttr(factory=self)

    def command_request(self, method, path):
        """
        Returns a callable request for a given http method and API path.
        You can then use this request to execute the command, and get
        the response value:

            >>> client = Client()
            >>> rqst = client.command_request('get', '/api/hcl')
            >>> resp, ok = rqst()

        Parameters
        ----------
        method : str
            the http method value, ['get', 'put', 'post', ...]

        path : str
            the API route string value, for example:
            "/api/resources/vlan-pools/{id}"

        Returns
        -------
        Request
            The request instance you can then use to exeute the command.
        """
        op = self.client.swagger_spec.get_op_for_request(method, path)
        if not op:
            raise RuntimeError(
                'no command found for (%s, %s)' % (method, path))

        return Request(self.client, CallableOperation(op))

    def path_requests(self, path):
        """
        Returns a Resource instace that will have attributes, one for each of the http-methods
        supported on that path.  For example:

            >>> client = Client()
            >>> hcl_api = client.path_requests('/api/hcl/{id}')
            >>> dir(hcl_api)
            [u'delete', u'get', u'put']

            >>> resp, ok = hcl_api.get(id='Arista_vEOS')

        Parameters
        ----------
        path : str
            The API path

        Returns
        -------
        Resource
            instance that has attributes for methods available.
        """
        path_spec = self.client.origin_spec['paths'].get(path)
        if not path_spec:
            raise RuntimeError("no path found for: %s" % path)

        get_for_meth = self.client.swagger_spec.get_op_for_request
        rsrc = BravadoResource(name=path, ops={
            method: get_for_meth(method, path)
            for method in path_spec.keys()})

        return RequestFactory.Resource(self.client, ResourceDecorator(rsrc))


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

    @staticmethod
    def proptype(prop_obj, prop_name):

        prop_info = prop_obj.propinfo(prop_name)
        if prop_info['type'] == 'array':
            prop = getattr(prop_obj, prop_name)
            if not prop:
                setattr(prop_obj, prop_name, [])
            return getattr(prop_obj, prop_name).__itemtype__

        return prop_info['type']

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

        return None

    def __call__(self, **params):
        """ execute the request and return the (response, ok) tuple """

        # auto-add body if exists and not provided by caller.
        if self.body_param and self.body_param not in params:
            params[self.body_param] = getattr(self, self.body_param).for_json()

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
