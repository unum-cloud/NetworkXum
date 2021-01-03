import copy

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

from PyStorageTexts.BaseAPI import BaseAPI
from PyStorageHelpers import *


class ElasticSearch(BaseAPI):
    """
        ElasticSearch is built on top of Lucene, but Lucene is  
        hard to install on its own. So we run the full version.

        https://www.elastic.co
        https://elasticsearch-py.readthedocs.io/en/master/
        https://www.elastic.co/guide/en/elasticsearch/reference/current/brew.html
    """
    __is_concurrent__ = False
    __max_batch_size__ = 100000
    __in_memory__ = False

# region Metadata

    def __init__(self, url='http://localhost:9200/text', **kwargs):
        BaseAPI.__init__(self, **kwargs)
        url, db_name = extract_database_name(url, default='text')
        self.elastic = Elasticsearch([url])
        self.db_name = db_name
        self.create_index()

    def count_texts(self) -> int:
        if not self.index_exists():
            return 0
        return self.elastic.count(index=self.db_name).pop('count', 0)

# region Random Writes

    def add(self, one_or_many_texts, upsert=True, sync=True) -> int:
        """
            https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-index_.html
        """
        if isinstance(one_or_many_texts, Text):
            result = self.elastic.index(index=self.db_name, id=one_or_many_texts._id, body={
                'content': one_or_many_texts.content,
            })
            result = result.pop('result', None)
            success = (result == 'created') or (result == 'updated')
            if sync and success:
                self.commit_all()
            return success
        elif is_sequence_of(one_or_many_texts, Text):
            statuses = [self.add(t, sync=False) for t in one_or_many_texts]
            cnt = int(sum(statuses))
            if sync and cnt:
                self.commit_all()
            return cnt

        return super().add(one_or_many_texts, upsert=upsert)

    def remove(self, one_or_many_texts, sync=True) -> int:
        if isinstance(one_or_many_texts, int):
            result = self.elastic.delete(
                index=self.db_name, id=one_or_many_texts)
            result = result.pop('result', None)
            success = (result == 'deleted')
            if sync and success:
                self.commit_all()
            return success
        elif is_sequence_of(one_or_many_texts, int):
            statuses = [self.remove(t, sync=False) for t in one_or_many_texts]
            cnt = int(sum(statuses))
            if sync and cnt:
                self.commit_all()
            return cnt

        return super().remove(one_or_many_texts)

# region Random Reads

    def get(self, identifier: int) -> Optional[Text]:
        """ 
            Returns the document together with it's system ID, that may be different from original one.
            It's done to reduce the DB size and accelerate the search.
            https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-get.html
        """
        result = self.elastic.get(index=self.db_name, id=identifier)
        if result and result.get('found', False):
            return self.parse_match(result)
        return None

    def find_substring(
        self,
        query: str,
        case_sensitive: bool = True,
        max_matches: Optional[int] = None,
        include_text=True,
    ) -> Sequence[TextMatch]:
        """
            https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-term-query.html
            https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-match-query.html
        """
        query_dict = {
            'query': {
                'match': {
                    'content': {
                        'query': query,
                        'operator': 'and',
                        'zero_terms_query': 'all',
                        'auto_generate_synonyms_phrase_query': False,
                    },
                },
            },
            'stored_fields': [],
        }
        # query_dict = {
        #     'query': {
        #         'match_phrase': {
        #             'content': query,
        #         },
        #     },
        #     'stored_fields': [],
        # }
        if max_matches:
            query_dict['from'] = 0
            query_dict['size'] = max_matches
        #
        result = self.elastic.search(index=self.db_name, body=query_dict)
        dicts = result.get('hits', {}).get('hits', [])
        return list(map(self.parse_match, dicts))

    def find_regex(
        self,
        query: str,
        case_sensitive: bool = True,
        max_matches: Optional[int] = None,
        include_text=True,
    ):
        """
            https://www.elastic.co/guide/en/elasticsearch/reference/6.8/query-dsl-regexp-query.html
            https://lucene.apache.org/core/4_9_0/core/org/apache/lucene/util/automaton/RegExp.html
        """
        query_dict = {
            'query': {
                'regexp': {
                    'content': {
                        'value': query,
                        'flags': 'INTERVAL',
                    },
                },
            },
            'stored_fields': [],
        }
        if max_matches:
            query_dict['from'] = 0
            query_dict['size'] = max_matches
        #
        result = self.elastic.search(index=self.db_name, body=query_dict)
        dicts = result.get('hits', {}).get('hits', [])
        return list(map(self.parse_match, dicts))

# region Bulk Reads

    @property
    def texts(self, page_size=100) -> Generator[Text, None, None]:
        offset = 0
        while True:
            result = self.elastic.search(index=self.db_name, body={
                "size": page_size,
                "from": offset
            })
            dicts = result.get('hits', {}).get('hits', [])
            if not dicts:
                break
            yield from map(self.parse_match, dicts)
            offset += page_size

# region Bulk Writes

    def add_stream(self, stream, upsert=False) -> int:
        """
            https://elasticsearch-py.readthedocs.io/en/master/helpers.html
        """
        cnt_success = 0
        if upsert:
            for t in stream:
                self.add(t, upsert=True, sync=False)
                cnt_success += 1
        else:
            def produce_validated():
                for t in stream:
                    yield t.__dict__
            for ok, action in streaming_bulk(
                client=self.elastic,
                index=self.db_name,
                actions=produce_validated(),
            ):
                cnt_success += ok
        #
        self.commit_all()
        return cnt_success

    def clear(self):
        """
            https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-exists.html
        """
        if self.index_exists():
            self.elastic.indices.delete(self.db_name)
        self.create_index()

# region Helpers

    def create_index(self):
        """
            https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-create-index.html
            https://sarahleejane.github.io/learning/python/2015/10/14/creating-an-elastic-search-index-with-python.html
        """
        if self.index_exists():
            return
        properties = dict()
        for field in self.indexed_fields:
            properties[field] = {'type': 'text'}
        self.elastic.indices.create(self.db_name, body={
            'settings': {
                'number_of_shards': 1,
            },
            'mappings': {
                'properties': properties,
            }
        })

    def index_exists(self):
        """
            https://www.elastic.co/guide/en/elasticsearch/reference/master/indices-exists.html
        """
        return self.elastic.indices.exists(self.db_name)

    def commit_all(self):
        return self.elastic.indices.refresh(self.db_name)

    def parse_match(self, hit: dict) -> TextMatch:
        return TextMatch(
            _id=int(hit.pop('_id', 0)),
            content=hit.pop('_source', {}).pop('content', ''),
            rating=float(hit.pop('_score', 1)),
        )


# region Testing

if __name__ == '__main__':
    sample_file = 'Datasets/text-test/nanoformulations.txt'
    db = ElasticSearch(url='http://localhost:9200/text-test')
    db.clear()
    assert db.count_texts() == 0
    assert db.add(Text.from_file(sample_file))
    assert db.count_texts() == 1
    assert db.find_substring('nanoparticles')
    assert db.find_regex('nanoparticles')
    assert db.remove(Text.from_file(sample_file))
    assert db.count_texts() == 0
