
import six
# noinspection PyPackageRequirements
from inflection import parameterize, underscore, camelize
from bravado_core.model import MODEL_MARKER

MODEL_NAME_SUFFIX = 'Body'


def humanize_api_path(api_path):
    """
    Converts an API path to a humaized string, for example:

        # >>> In [2]: humanize_api_path('/api/vlan/{id}')
        # >>> Out[2]: u'ApiVlanId'


    Parameters
    ----------
    api_path : str
        An API path string.

    Returns
    -------
    str - humazined form.
    """
    return reduce(lambda val, func: func(val),
                  [parameterize, underscore, camelize],
                  unicode(api_path))


def modeltag_nonref_schemas(spec):
    """
    This function will go through the OpenAPI 'paths' and look for any
    command parameters that have non "$ref" schemas defined.  If the
    parameter does have a $ref schema, then the bravado library will
    do this x-model tagging.  But it does not do it for schemas that
    are defined inside the path/command structure

    Parameters
    ----------
    spec : dict
        The OpenApi spec dictionary
    """

    for path_name, path_data in six.iteritems(spec['paths']):
        for path_cmd, cmd_data in six.iteritems(path_data):

            # check the parameters, looking for "schemas" that
            # do not have $ref or already tagged.  when found
            # use either the operationId or the (command, api-path)
            # to formulate a humanized tag name.

            for param in cmd_data.get('parameters'):
                schema = param.get('schema')
                if schema and ('$ref' not in schema) and (MODEL_MARKER not in schema):
                    model_name = (camelize(cmd_data.get('operationId')) or
                                  "%s%s" % (path_cmd.upper(),
                                            humanize_api_path(path_name)))

                    schema[MODEL_MARKER] = "%s%s" % (model_name, MODEL_NAME_SUFFIX)

            # not sure if we need to check responses ...
            # but if so, we would add the code here. <TBD>


def assign_operation_ids(spec, operids):
    """ used to assign caller provided operationId values into a spec """

    empty_dict = {}

    for path_name, path_data in six.iteritems(spec['paths']):
        for method, method_data in six.iteritems(path_data):
            oper_id = operids.get(path_name, empty_dict).get(method)
            if oper_id:
                method_data['operationId'] = oper_id
