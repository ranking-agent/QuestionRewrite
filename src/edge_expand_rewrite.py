from copy import deepcopy
import sqlite3
import os
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
    """Given a predicate going from type a to type b, find the edges that you can expand or
    replace it with, along with their statistics"""
    apath = os.path.dirname(os.path.abspath(__file__))
    fname = f'{apath}/{expander}'
    print(fname)
    with sqlite3.connect(fname) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute('SELECT expansions, pcaconfidence, headcoverage from expansions where source_type=? and edge_type=? and target_type=?',
                     (source_type, edge_type, target_type))
        results = cur.fetchall()
    return results
