from elasticsearch import Elasticsearch

from PyWrappedDocs.BaseAPI import BaseAPI
from PyWrappedHelpers.Algorithms import *
from PyWrappedHelpers.TextFile import TextFile


class ElasticSearch(BaseAPI):
    """
        ElasticSearch is built on top of Lucene, but Lucene is very 
        hard to install on its own. So we run the full version.

        https://www.elastic.co
        https://elasticsearch-py.readthedocs.io/en/master/
        https://www.elastic.co/guide/en/elasticsearch/reference/current/brew.html
    """
    __is_concurrent__ = False
    __max_batch_size__ = 1000000
    __in_memory__ = False

    def __init__(self, url='http://localhost:9200', db_name='text', **kwargs):
        BaseAPI.__init__(self, **kwargs)
        self.elastic = Elasticsearch([url])
        self.db_name = db_name
        self.create_index()

    def create_index(self):
        # https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-exists.html
        if self.index_exists():
            return
        properties = dict()
        for field in self.indexed_fields:
            properties[field] = {'type': 'text'}
        # https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-create-index.html
        # https://sarahleejane.github.io/learning/python/2015/10/14/creating-an-elastic-search-index-with-python.html
        self.elastic.indices.create(self.db_name, body={
            'settings': {
                'number_of_shards': 1,
            },
            'mappings': {
                'properties': properties,
            }
        })

    def index_exists(self):
        return self.elastic.indices.exists(self.db_name)

    def commit_all(self):
        return self.elastic.indices.refresh(self.db_name)

    def remove_all(self):
        # https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-exists.html
        if self.index_exists():
            self.elastic.indices.delete(self.db_name)
        self.create_index()

    def count_docs(self) -> int:
        if not self.index_exists():
            return 0
        return self.elastic.count(index=self.db_name).pop('count', 0)

    def upsert_doc(self, doc, sync=True) -> bool:
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-index_.html
        doc_id = doc.pop('_id', None)
        if doc_id is None:
            return False
        result = self.elastic.index(index=self.db_name, id=doc_id, body=doc)
        result = result.pop('result', None)
        if (result == 'created') or (result == 'updated'):
            if sync:
                self.commit_all()
            return True
        return False

    def remove_doc(self, doc, sync=True) -> bool:
        doc_id = doc.pop('_id', None)
        if doc_id is None:
            return False
        result = self.elastic.delete(index=self.db_name, id=doc_id)
        result = result.pop('result', None)
        if (result == 'deleted'):
            if sync:
                self.commit_all()
            return True
        return False

    def find_with_id(self, identifier: str):
        return self.elastic.get(index=self.db_name, id=identifier)

    def find_with_substring(self, query: str, field: str = 'plain'):
        # https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-term-query.html
        docs = self.elastic.search(index=self.db_name, body={
            'query': {
                'term': {
                    field: query,
                }
            }
        })
        return docs['hits']

    def find_with_regex(self, query: str, field: str = 'plain'):
        # https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-regexp-query.html
        # https://lucene.apache.org/core/4_9_0/core/org/apache/lucene/util/automaton/RegExp.html
        docs = self.elastic.search(index=self.db_name, body={
            'query': {
                'regexp': {
                    field: {
                        'value': query,
                        'flags': 'INTERVAL',
                    }
                }
            }
        })
        return docs['hits']


if __name__ == '__main__':
    sample_file = 'Datasets/text-test/nanoformulations.txt'
    db = ElasticSearch(url='http://localhost:9200/',
                       db_name='text-test')
    db.remove_all()
    assert db.count_docs() == 0
    assert db.upsert_doc(TextFile(sample_file).to_dict())
    assert db.count_docs() == 1
    assert db.find_with_substring('nanoparticles')
    assert db.find_with_regex('nanoparticles')
    assert db.remove_doc(TextFile(sample_file).to_dict())
    assert db.count_docs() == 0
