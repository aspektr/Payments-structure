from sqlalchemy import create_engine
import pandas as pd
import networkx as nx
import logging
from matplotlib import pyplot as plt


logging.basicConfig(level=logging.INFO)

typedb = 'postgresql'
host = '127.0.0.1'
port = 5432
user = 'user'
psw = 'password'
schema = 'public'

from_db = typedb, user, psw, host, port, schema
with_query = "select sender_inn, receiver_inn from documents"


def test_connected_components():
    print("Test networkx libarary connected_components: ", end='')
    # nodes are:
    a, b, c, d, e, f, g = 'A', 'B', 'C', 'D', 'E', 'F', 'G'
    graph = nx.Graph()
    graph.add_edges_from([(a, b), (b, c), (c, d), (a, c), (e, f), (f, g), (e, g)])
    connected_components = sorted(nx.connected_components(graph), key=len, reverse=True)
    print("OK") if connected_components[0] == {a, b, c, d} and connected_components[1] == {e, f, g} else print("Failed")


def test_cycles():
    print("Test networkx libarary cycles: ", end='')
    # nodes are:
    a, b, c, d, e, f, g = 'A', 'B', 'C', 'D', 'E', 'F', 'G'
    graph = nx.Graph()
    graph.add_edges_from([(a, b), (b, c), (c, d), (a, c), (e, f), (f, g)])
    cycles = sorted(nx.cycle_basis(graph), key=len, reverse=True)
    print("OK") if set(cycles[0]) == {a, b, c} else print("Failed")


def get_data(connection_string: tuple, query_db: str):
    engine = create_engine('%s://%s:%s@%s:%s/%s' % connection_string)
    res = pd.read_sql_query(query_db, con=engine)
    res = res.drop_duplicates()
    logging.info("Data from db has loaded successfully")
    logging.info("DataFrame size is %s x %s" % (res.shape[0], res.shape[1]))
    return res


def create_graph(df: pd.DataFrame):
    g = nx.Graph()
    g.add_edges_from(df.values)
    logging.info("Creating graph has finished successfully")
    return g


def create_orgraph(df: pd.DataFrame):
    g = nx.DiGraph()
    g.add_edges_from(df.values)
    logging.info("Creating orgraph has finished successfully")
    return g


def find_connected_components(G: nx.Graph):
    res = sorted(nx.connected_components(G), key=len, reverse=True)
    logging.info("Number of connected components = %d" % len(res))
    return res


def find_strongly_connected_components(G: nx.Graph):
    res = sorted(nx.strongly_connected_components(G), key=len, reverse=True)
    logging.info("Number of strongly connected components = %d" % len(res))
    return res


def count_connected_components(connected_components: list):
    # create dict where key=> a size of connected_components; value=> a number of such connected_components
    connected_component_rating = {}
    for each_connected_component in connected_components:
        size = len(each_connected_component)
        connected_component_rating[size] = connected_component_rating[size] + 1 if size in connected_component_rating else 1
    logging.info("Counting of connected components has finished successfully")
    return connected_component_rating


def sort_connected_components(connected_component_rating: dict):
    return [(size, connected_component_rating[size]) for size in sorted(connected_component_rating, reverse=True)]


if __name__ == '__main__':
    # run test
    test_connected_components()
    test_cycles()

    # get data
    from_df = get_data(from_db, with_query)

    # create undirected simple graph
    transaction_graph = create_graph(from_df)

    # find connected components
    connected_components = find_connected_components(transaction_graph)
    connected_component_rating = count_connected_components(connected_components)
    top = sort_connected_components(connected_component_rating)
    print("CONNECTED COMPONENTS")
    print(pd.DataFrame(top, columns=['size of connected component', 'quantity of such components']), )

    # find bridges
    node_from_biggest_connected_component = list(connected_components[0])[0]
    bridges = list(nx.bridges(transaction_graph, node_from_biggest_connected_component))
    print("Number of bridges is %s" % len(bridges))

    # create directed graph with self loops
    orgraph = create_orgraph(from_df)

    # find strongly connected components
    strongly_connected_components = find_strongly_connected_components(orgraph)
    strongly_connected_component_rating = count_connected_components(strongly_connected_components)
    top = sort_connected_components(strongly_connected_component_rating)
    print("STRONGLY CONNECTED COMPONENTS")
    print(pd.DataFrame(top, columns=['size of strongly connected component', 'quantity of such components']))

    # find the biggest strongly connected component
    biggest_strongly_connected_components = list(strongly_connected_components[0])

    # prepare sql query to extract transactions related with strongly connected components
    with_query = "select distinct * from (select sender_name, receiver_name, sender_inn, receiver_inn from document where sender_inn in (" +\
        ", ".join(["'" + x + "'" for x in biggest_strongly_connected_components])+ \
                 ") and receiver_inn in (" + \
        ", ".join(["'" + x + "'" for x in biggest_strongly_connected_components])+ \
        "))a where sender_inn <> receiver_inn"
    from_df = get_data(from_db, with_query)
    orgraph = create_orgraph(from_df[['sender_name', 'receiver_name']])
    nx.draw(orgraph, with_labels=False)
    plt.show()


