
from bravado_core. resource import Resource as BravadoResource
from bravado.client import CallableOperation, ResourceDecorator

from .request import Request


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

        def __repr__(self):
            return str(dir(self))


    class ViaAttr(object):
        def __init__(self, factory):
            self._factory = factory

        def __getattr__(self, attr):
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
