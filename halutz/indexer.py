from first import first
from bidict import namedbidict
import six
import json
from operator import itemgetter

class Indexer(object):

    FROM_KEY = None
    Index = namedbidict('Index', 'id', 'name')

    def __init__(self, rqst, name_from=None, id_from=None, response_code='200'):
        self.rqst = rqst

        deref = rqst.client.deref
        self.schema = deref(rqst.spec['responses'][response_code]['schema'])
        assert self.schema['type'] == 'object', "response is not an object type"

        s_props = self.schema['properties']
        self.items_key = first(s_props)

        items_schema = s_props[self.items_key]

        items_type = items_schema['type']
        assert items_type in ['object', 'array'], "unknown items type: %s" % items_type

        if items_type == 'object':
            self.items_properties = (
                items_schema.get('properties') or
                items_schema['additionalProperties']['properties'])

            self._ingest_ = self.ingest_from_dict
        else:
            self.items_properties = items_schema['items']['properties']
            self._ingest_ = self.ingest_from_list

        self.name_from = name_from
        self.id_from = id_from
        self.items_type = items_type
        self.index = Indexer.Index()
        self.catalog = dict()

    @property
    def names(self):
        return self.index.id_for.keys()

    @property
    def ids(self):
        return self.index.name_for.keys()

    def ingest_from_dict(self, items):

        # if id_from is None, then we use the key as the id
        # otherwise we have a property identified to get the id value

        if not self.id_from:
            def id_from(key, _value):
                return key
        else:
            def id_from(_key, value):
                return value[self.id_from]

        # if name_from is None, then we use the key as the name
        # value, otherwise we have a property identified to get
        # the name value

        if not self.name_from:
            def name_from(key, _value):
                return key
        else:
            def name_from(_key, value):
                return value[self.name_from]

        for each_key, each_item in six.iteritems(items):
            each_id = id_from(each_key, each_item)
            each_name = name_from(each_key, each_item)
            self.index[each_id] = each_name
            self.catalog[each_id] = each_item

    def ingest_from_list(self, items):
        id_from = itemgetter(self.id_from or 'id')
        name_from = itemgetter(self.name_from or 'name')
        for each_item in items:
            each_id = id_from(each_item)
            each_name = name_from(each_item)
            self.index[each_id] = each_name
            self.catalog[each_id] = each_item

    def clear(self):
        self.index.clear()
        self.catalog.clear()

    def get(self, **kwargs):
        resp, ok = self.rqst(**kwargs)
        if not ok:
            raise RuntimeError(
                'unable to get items', resp)

        self.clear()
        self._ingest_(resp[self.items_key])

        return self

    def __getitem__(self, item_name):
        item_id = self.index.id_for.get(item_name)
        assert item_id, "item name %s not found in catalog" % item_name
        return item_id, self.catalog[item_id]

    def __len__(self):
        return len(self.index)

    def __contains__(self, item_name):
        return item_name in self.index.id_for

    def __repr__(self):
        return json.dumps({
            'path': self.rqst.path,
            'count': len(self.index),
            'names': self.names
        }, indent=3)
