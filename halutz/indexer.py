import six
import copy
from pprint import pformat
from first import first
from bidict import namedbidict
from operator import itemgetter
from collections import namedtuple


__all__ = ['Indexer', 'IndexItem']


class IndexItem(object):
    def __init__(self, item_id, item_name, item_value, index):
        self.id, self.name, self.value = item_id, item_name, item_value
        self.index = index

    def __repr__(self):
        return pformat({
            'id': self.id,
            'name': self.name,
            'value': self.value})


class Indexer(object):
    RESP_STATUS_CODE = '200'
    Index = namedbidict('Index', 'id', 'name')
    index_item_type = IndexItem

    def __init__(self, rqst,
                 name_from=None,
                 id_from=None,
                 response_code=None,        # will use default if set to None
                 index_item_type=None       # will use default if None
                 ):

        self.rqst = rqst
        self.name_from = name_from
        self.id_from = id_from

        deref = rqst.client.deref

        self.schema = deref(rqst.spec['responses'][response_code or Indexer.RESP_STATUS_CODE]['schema'])
        assert self.schema['type'] == 'object', "response is not an object type"

        s_props = self.schema['properties']
        self.items_key = first(s_props)

        items_schema = s_props[self.items_key]

        items_type = items_schema['type']
        assert items_type in ['object', 'array'], "unknown items type: %s" % items_type

        if items_type == 'object':
            self._ingest_ = self.ingest_from_dict
            self.items_properties = (
                items_schema.get('properties') or
                items_schema['additionalProperties']['properties'])
        else:
            self._ingest_ = self.ingest_from_list
            self.items_properties = (
                items_schema['items'].get('properties') or
                deref(items_schema['items']))

        self.items_type = items_type
        self.index = Indexer.Index()
        self.index_item_type = index_item_type or IndexItem
        self.catalog = dict()
        self.run_kwargs = None

    @property
    def names(self):
        # TODO: change to list(self.index.id_for) validate is list for Py2 and Py3
        return self.index.id_for.keys()

    @property
    def ids(self):
        # TODO: change to list(self.index.id_for) validate is list for Py2 and Py3
        return self.index.name_for.keys()

    def ingest_from_dict(self, items):
        # if id_from is None, then we use the key as the id
        # otherwise we have a property identified to get the id value

        if not callable(self.id_from):
            if not self.id_from:
                self.id_from = lambda k, v: k
            else:
                self.id_from = lambda k, v: v[self.id_from]

        # if name_from is None, then we use the key as the name
        # value, otherwise we have a property identified to get
        # the name value

        if not callable(self.name_from):
            if not self.name_from:
                self.name_from = lambda k, v: k
            else:
                self.name_from = lambda k, v: v[self.name_from]

        for each_key, each_item in six.iteritems(items):
            each_id = self.id_from(each_key, each_item)
            each_name = self.name_from(each_key, each_item)
            self.index[each_id] = each_name
            self.catalog[each_id] = each_item

    def ingest_from_list(self, items):
        if not callable(self.id_from):
            self.id_from = itemgetter(self.id_from or 'id')

        if not callable(self.name_from):
            self.name_from = itemgetter(self.name_from or 'name')

        for each_item in items:
            each_id = self.id_from(each_item)
            each_name = self.name_from(each_item)
            self.index[each_id] = each_name
            self.catalog[each_id] = each_item

    def clear(self):
        self.index.clear()
        self.catalog.clear()

    def run(self, **kwargs):
        # keep a copy of the last run kwargs so that they could be later referenced
        # this is usedful for URL construction/ect.

        self.run_kwargs = copy.deepcopy(kwargs)

        resp, ok = self.rqst(**kwargs)
        if not ok:
            raise RuntimeError(
                'unable to get items', resp)

        items = resp[self.items_key]

        self.clear()
        self._ingest_(items)

        return self

    def rerun(self):
        return self.run(**self.run_kwargs)

    def find(self, item_name):
        return None if item_name not in self else self[item_name]

    def __iter__(self):
        myself = self

        class IndexIterator(object):
            def __init__(self):
                self._name_iter = iter(myself.index.id_for)

            def next(self):
                return myself[six.next(self._name_iter)]

            __next__ = next

        return IndexIterator()

    def __getitem__(self, item_name):
        item_id = self.index.id_for.get(item_name)
        assert item_id, "item name %s not found in catalog" % item_name

        return self.index_item_type(
            item_id=item_id, item_name=item_name,
            item_value=self.catalog[item_id],
            index=self)

    def __len__(self):
        return len(self.index)

    def __contains__(self, item_name):
        return item_name in self.index.id_for

    def __repr__(self):
        return pformat({
            'path': self.rqst.path,
            'count': len(self.index),
            'names': self.names})
