from elasticsearch import Elasticsearch

from PyWrappedDocs.BaseAPI import BaseAPI
from PyWrappedGraph.Algorithms import *
from PyWrappedDocs.File import File


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

    def __init__(self, url='http://localhost:9300', **kwargs):
        BaseAPI.__init__(self, url, **kwargs)
        self.elastic = Elasticsearch([url])
        self.db_name = extract_database_name(url)
        self.create_index()
            

    def create_index(self):
        # https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-exists.html
        if self.elastic.exists(self.db_name):
            return
            
        properties = dict()
        for field in self.indexed_fields:
            properties[field] = { 'type': 'text' }
        # https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-create-index.html
        self.elastic.create(self.db_name, body={
            'settings' : {
                'number_of_shards' : 1,
            },
            'mappings' : {
                'properties': properties,
            }
        })

    def cound_docs(self):
        return self.elastic.count(index=self.db_name)

    def upsert_doc(self, doc):
        result = self.elastic.index(index=self.db_name, id=doc['_id'], body=doc)
        return result

    def remove_doc(self, doc):
        result = self.elastic.delete(index=self.db_name, id=doc['_id'])
        return result

    def find_by_id(self, identifier:str):
        return self.elastic.get(index=self.db_name, id=identifier)

    def find_with_substring(self, field, query):
        # https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-term-query.html
        return self.elastic.search(index=self.db_name, body={
            'query': {
                'term': {
                    field: query,
                }
            }
        })

    def find_with_regex(self, field, query):
        # https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-regexp-query.html
        # https://lucene.apache.org/core/4_9_0/core/org/apache/lucene/util/automaton/RegExp.html
        return self.elastic.search(index=self.db_name, body={
            'query': {
                'regexp': {
                    field: query,
                    'flags': 'INTERVAL',
                }
            }
        })


if __name__ == '__main__':
    sample_file = 'datasets/nlp/paper.json'
    es = ElasticSearch()
    assert es.cound_docs() == 0
    assert es.upsert_doc(File(sample_file).content)
    assert es.cound_docs() == 1
    es.remove_all()
    assert es.cound_docs() == 0
