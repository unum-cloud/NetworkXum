from elasticsearch import Elasticsearch

from PyWrappedDocs.BaseAPI import BaseAPI


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
