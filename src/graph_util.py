from collections import defaultdict

def get_node(graph, node_id):
    """Return the node from the graph that has the given node"""
    for n in graph['nodes']:
        if n['id'] == node_id:
            return n
    return None


def get_edge(graph,edge_id):
    """Return the node from the graph that has the given node"""
    for n in graph['edges']:
        if n['id'] == edge_id:
            return n
    return None

def get_source_type(graph, edge_id):
    edge = get_edge(graph,edge_id)
    source_id = edge['source_id']
    return get_node(graph,source_id)['type']

def get_target_type(graph, edge_id):
    edge = get_edge(graph,edge_id)
    source_id = edge['target_id']
    return get_node(graph,source_id)['type']

def remove_edge(graph, edge_id):
    for edge in graph['edges']:
        if edge['id'] == edge_id:
            redge = edge
    graph['edges'].remove(redge)
    return redge

def print_linear_graph(graph):
    #Assuming that the graph is linear, write a cypherlike version
    #First find a loose edge
    if graph.get('machine_question') is not None:
        graph = graph['machine_question']

    nconnections = defaultdict(int)
    for e in graph['edges']:
        nconnections[e['source_id']] += 1
        nconnections[e['target_id']] += 1
    for k,v in nconnections.items():
        if v == 1:
            break
    cnodeid = k
    #Now follow the path
    cnode = get_node(graph,cnodeid)
    s=f'({cnode["type"]})'
    unwritten_edges = set( [e['id'] for e in graph['edges']])
    while len(unwritten_edges) > 0:
        for eid in unwritten_edges:
            e = get_edge(graph,eid)
            if cnodeid == e['source_id']:
                s += f"-[{e['type']}]->"
                cnodeid = e['target_id']
                unwritten_edges.remove(eid)
                break
            if cnodeid == e['target_id']:
                s += f"<-[{e['type']}]-"
                cnodeid = e['source_id']
                unwritten_edges.remove(eid)
                break
        #walked all the edges, we done.
        cnode = get_node(graph,cnodeid)
        s += f'({cnode["type"]})'
    return s


