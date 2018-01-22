
from first import first
from copy import deepcopy

from jsonschema.compat import lru_cache
from python_jsonschema_objects import ObjectBuilder
from python_jsonschema_objects.classbuilder import ClassBuilder

__all__ = ['SchemaObjectFactory']


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
    def proptype(prop_obj, prop_name):
        prop_info = prop_obj.propinfo(prop_name)

        if prop_info['type'] == 'array':
            # if the prop does not exist, then we need to lazy create it
            # so we can get the item type from the __itemtype__ attribute

            prop = getattr(prop_obj, prop_name)
            if not prop:
                setattr(prop_obj, prop_name, [])
            return getattr(prop_obj, prop_name).__itemtype__

        prop_type = prop_info['type']
        return {
            'integer': int,
            'string': str,
            'object': dict
        }.get(prop_type, prop_type)

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
        model_cls.proptype = SchemaObjectFactory.proptype
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
