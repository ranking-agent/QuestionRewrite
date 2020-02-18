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
