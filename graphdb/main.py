from rocks_nested import *
from rocks_adjacency import *
from mongo_adjacency import *
from sqlite_adjacency import *

def insert_separate(db, edges):
    # Measure time spent for each seprate insert
    pass
    
def insert_batched(db, edges, batch_size):
    # Split data into groups and pass like that
    pass

def remove_random_edges(db, edges)




def main(filename):
    # Select this data beforehand to:
    # - avoid affecting the runtime of benchmark.
    # - perform same "random" operations on different DBs.
    edges_to_insert_separately = []
    edges_to_insert_batched = []
    edges_to_lookup_sequential = []
    edges_to_lookup_random = []
    nodes_to_lookup_relations = []
    nodes_to_lookup_from = []
    nodes_to_lookup_to = []
    nodes_to_lookup_friends_of_friends = []
    nodes_to_compute_degree = []
    nodes_to_compute_weight = []
    edges_remove_separately = []
    edges_remove_separately = []