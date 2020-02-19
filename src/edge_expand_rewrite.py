from copy import deepcopy
from src.graph_util import get_edge, get_source_type, get_target_type

def rewrite_edge_expand(machine_question, expanders=['amie_v1'], depth =1):
    """Given a machine question, apply edge expansions from a set of expanders.
    This can be iteratively applied for *depth* times.  Passing in a single edge
    with depth=1 produces a two-hop question, and depth=2 will produce 3 hop
    questions, and also return the intermediate 2 hops."""
    to_expand = [machine_question]
    if depth < 1:
        return []
    for d in range(depth):
        newquestions = []
        for starting_q in to_expand:
            for edge in starting_q['edges']:
                for expander in expanders:
                    newquestions.append( edge_expand(starting_q, edge['id'], expander) )
    return []

def edge_expand(input_query, edge_id, expander):
    """Given an input query and an edge id, lookup the expansions
    for that edge, apply them to the query and a list of expansion
    results."""
    output_query = deepcopy(input_query)
    edge = get_edge(output_query,edge_id)
    source_type = get_source_type(output_query, edge_id)
    target_type = get_target_type(output_query, edge_id)
    replacements = lookup_edge_expansions(expander, source_type, edge['type'], target_type)
    return [output_query]

def lookup_edge_expansions(expander, source_type, edge_type, target_type):
    return []