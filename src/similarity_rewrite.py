from copy import deepcopy

from src.graph_util import get_node, get_edge


def similarity_expand(querygraph, expansion_types=['chemical_substance']):
    """Takes a ReasonerStd Query Graph, and creates new graphs by doing available
    similarity expansions.  In the prototype, only chemical_substance is available."""
    #Find the nodes that can be expanded
    enodes = []

    if querygraph.get('machine_question') is not None:
        querygraph = querygraph['machine_question']

    for node in querygraph['nodes']:
        if node['type'] in expansion_types:
            enodes.append(node['id'])
    #Now we iterate over these nodes.  At each node, we create new partial graphs, by
    # applying the expand operation or not to all ove the previous partial graphs.
    # The expand operation will return new partial graphs for every path coming off of
    # the node in question.
    partials = [querygraph]
    for expand_node in enodes:
        newpartials = []
        for partial in partials:
            newpartials += apply_node_expansion(partial,expand_node)
        partials += newpartials
    #Don't return the original query
    return partials[1:]

def apply_node_expansion(query_graph,expand_node_id):
    """Given a querygraph and an node to similarity expand, return new graphs where
    the node is expanded.  If the degree of the expansion node is D, then then we should
    return a list of (2**D)-1 new graphs."""
    #Suppose that there are 2 edges coming into a node
    # A - B - C.  Then we want to return A - B - B' - C
    # But if there are 3, like A-B-C, B-D, then it's possible that we need to similarity
    # expand to get B to C and / or to get to B-D, so that means we have to manage
    # the combinations.
    #First, what edges do we need to expand into?
    edge_cands = []

    for edge in query_graph['edges']:
        if expand_node_id == edge['source_id'] or expand_node_id == edge['target_id']:
            edge_cands.append(edge['id'])
    #If there's more than one edge, we can drop one , doesn't matter which
    if len(edge_cands) > 1:
        edge_cands=edge_cands[1:]
    # now we have to play the same game of combinatorics
    partials = [query_graph]
    for edge_id in edge_cands:
        newpartials = []
        for partial in partials:
            newpartial = apply_node_expansion_along_edge(partial,edge_id,expand_node_id)
            newpartials.append(newpartial)
        partials += newpartials
    #Don't include the original query graph
    return partials[1:]

def apply_node_expansion_along_edge(query_graph,edge_id,node_id):
    """Given a query graph, a node, and an edge to/from that node, create a new node,
    connected to the original node via a similarity edge, and attach the old edge to that
    new node.
    i.e. given A-[x1]-B-[x2]-C, B, x2, return A-[x1]-B-[sim]-B'-[x2]-C.
    All other edges to B remain attached to B."""
    new_graph = deepcopy(query_graph)
    simnode_id = add_sim_node(node_id,new_graph)
    edge = get_edge(new_graph, edge_id)
    if edge['source_id'] == node_id:
        edge['source_id'] = simnode_id
    elif edge['target_id'] == node_id:
        edge['target_id'] = simnode_id
    else:
        raise Exception('The input edge does not connect to the input node')
    new_edge_id = generate_novel_sim_edge_id(new_graph)
    new_graph['edges'].append( {'id': new_edge_id, 'source_id': node_id, 'target_id': simnode_id})
    return new_graph

def add_sim_node(n_id,g):
    """Given a graph g, and a node n from that graph, make a new node n'
    which is a copy of node n, but with a unique id, and add it to the graph."""
    n = get_node(g, n_id)
    nprime = deepcopy(n)
    new_id = generate_novel_sim_id(n,g)
    nprime['id'] = new_id
    g['nodes'].append(nprime)
    return new_id

def generate_novel_sim_id(n,g):
    node_ids = [n['id'] for n in g['nodes']]
    uid = 0
    nid = f"sim_to_{n['id']}_{uid}"
    while nid in node_ids:
        uid += 1
        nid = f"sim_to_{n['id']}_{uid}"
    return nid

def generate_novel_sim_edge_id(g):
    edge_ids = set([e['id'] for e in g['edges']])
    uid = 0
    eid = f'sim_edge_{uid}'
    while eid in edge_ids:
        uid += 1
        eid = f'sim_edge_{uid}'
    return eid

