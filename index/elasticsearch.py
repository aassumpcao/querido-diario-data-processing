from typing import List
import os

import elasticsearch

from tasks import IndexInterface


class ElasticSearchInterface(IndexInterface):
    def __init__(self, hosts: List, timeout: str = "30s", default_index: str = None):
        self._es = elasticsearch.Elasticsearch(hosts=hosts)
        self._timeout = timeout
        self._default_index = default_index

    def index_exists(self, index_name: str) -> bool:
        return self._es.indices.exists(index=index_name)

    def is_valid_index_name(self, index_name: str) -> bool:
        return isinstance(index_name, str) and len(index_name) > 0

    def get_index_name(self, index_name: str) -> str:
        if self.is_valid_index_name(index_name):
            return index_name
        if self._default_index is None:
            raise Exception("Index name not defined")
        return self._default_index

    def create_index(self, index_name: str = None) -> None:
        index_name = self.get_index_name(index_name)
        if self.index_exists(index_name):
            return
        self._es.indices.create(
            index=index_name,
            body={"mappings": {"properties": {"date": {"type": "date"}}}},
            timeout=self._timeout,
        )

    def index_document(self, document, index: str = None) -> None:
        index = self.get_index_name(index)
        result = self._es.index(
            index=index, body=document, id=document["file_checksum"]
        )


def get_elasticsearch_host():
    return os.environ["ELASTICSEARCH_HOST"]


def get_elasticsearch_index():
    return os.environ["ELASTICSEARCH_INDEX"]


def create_index_interface() -> IndexInterface:
    hosts = get_elasticsearch_host()
    if not isinstance(hosts, str) or len(hosts) == 0:
        raise Exception("Missing index hosts")
    default_index_name = get_elasticsearch_index()
    if not isinstance(default_index_name, str) or len(default_index_name) == 0:
        raise Exception("Invalid index name")
    return ElasticSearchInterface([hosts], default_index=default_index_name)
