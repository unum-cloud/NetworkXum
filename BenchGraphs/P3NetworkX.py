import networkx as nx
from PyStorageGraph.MongoDB import MongoDB

G = MongoDB(url='mongodb://localhost:27017/communitiesfb',
            directed=False, multigraph=False)
comps = nx.average_clustering(G)
print(comps)
