from copy import deepcopy
import sqlite3
import os
from ast import literal_eval
from src.graph_util import get_edge, get_source_type, get_target_type, remove_edge
import pandas as pd
import numpy as np

def rewrite_edge_expand(machine_question, expanders=['amie_v1.db'], depth =1):
    """Given a machine question, apply edge expansions from a set of expanders.
    This can be iteratively applied for *depth* times.  Passing in a single edge
    with depth=1 produces a two-hop question, and depth=2 will produce 3 hop
    questions, and also return the intermediate 2 hops."""

    if machine_question.get('machine_question') is not None:
        machine_question = machine_question['machine_question']

    to_expand = [machine_question]
    if depth < 1:
        return []
    retquestions = []
    for d in range(depth):
        newquestions=[]
        for starting_q in to_expand:
            for edge in starting_q['edges']:
                for expander in expanders:
                    newquestions +=  edge_expand(starting_q, edge['id'], expander)
        retquestions += newquestions
        to_expand = newquestions
    return retquestions

def edge_expand(input_query, edge_id, expander):
    """Given an input query and an edge id, lookup the expansions
    for that edge, apply them to the query and a list of expansion
    results."""
    edge = get_edge(input_query,edge_id)
    source_type = get_source_type(input_query, edge_id)
    target_type = get_target_type(input_query, edge_id)
    replacements = lookup_edge_expansions(expander, source_type, edge['type'], target_type)
    rwp = add_pareto_values(replacements)
    best = rwp[ rwp['Pareto'] == 1].copy()
    newqs = []
    for index,row in best.iterrows():
        expansion = literal_eval(row['expansions'])
        output_query = deepcopy(input_query)
        replace_edge(output_query,edge_id,expansion)
        newqs.append(output_query)
    return newqs

def replace_edge(query,edge_id,expansion):
    """Given a machine question replace the edge specified by edge_id, and replace
    it with the expansion"""
    #This function feels pretty crufty, split it up, move some to graph_utils, I think.
    old_edge = remove_edge(query,edge_id)
    remaps = {'a': old_edge['source_id'], 'b': old_edge['target_id']}
    for node in expansion['nodes']:
        if node['id'] not in ['a','b']:
            #THere's a new intermediary node.  Add it into the graph
            #Make sure to get a unique node identifier
            node_ids = set([ e['id'] for e in query['nodes'] ])
            ncount = 0
            nid = f'expansion_node_{ncount}'
            while nid in node_ids:
                ncount += 1
                nid = f'expansion_node_{ncount}'
            #keep track of how we're renaming, b/c we need to update the edges
            remaps[node['id']] = nid
            node['id'] = nid
            query['nodes'].append(node)
            node_ids.add(nid)
    for newedge in expansion['edges']:
        for node_key in ['source_id', 'target_id']:
            original_node_id = newedge[node_key]
            if original_node_id in remaps:
                newedge[node_key] = remaps[original_node_id]
    #add the new edge(s)
    edge_ids = set([ e['id'] for e in query['edges'] ])
    ecount = 0
    for edge in expansion['edges']:
        eid = f'expansion_edge_{ecount}'
        while eid in edge_ids:
            ecount += 1
            eid = f'expansion_edge_{ecount}'
        edge['id'] = eid
        query['edges'].append(edge)
        edge_ids.add(eid)
    return query


def lookup_edge_expansions(expander, source_type, edge_type, target_type):
    """Given a predicate going from type a to type b, find the edges that you can expand or
    replace it with, along with their statistics"""
    apath = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(apath,'rule_databases',expander)
    if not os.path.exists(fname):
        print(f"Missing expander {fname}")
        raise Exception('Missing expander')
    with sqlite3.connect(fname) as conn:
        conn.row_factory = sqlite3.Row
        df = pd.read_sql_query('SELECT expansions, pcaconfidence, headcoverage from expansions where source_type=? and edge_type=? and target_type=?',
                     conn, params =(source_type, edge_type, target_type))
    return df

def is_pareto_efficient_simple(costs):
    """ Find the pareto-efficient points
      :param costs: An (n_points, n_costs) array
      :return: A (n_points, ) boolean array, indicating whether each point is Pareto efficient
      """
    is_efficient = np.ones(costs.shape[0], dtype = bool)
    for i, c in enumerate(costs):
        if is_efficient[i]:
            is_efficient[is_efficient] = np.any(costs[is_efficient]<c, axis=1)  # Keep any point with a lower cost
            is_efficient[i] = True  # And keep self
    return is_efficient

def add_pareto_values(inframe):
    inframe['Pareto'] = 0
    n = 1
    inframe['imprecision']=1-inframe['headcoverage']
    inframe['unconfidence']=1-inframe['pcaconfidence']
    while len( inframe[inframe['Pareto'] == 0]) > 0:
        dg = inframe[ ['imprecision','unconfidence'] ]
        costs = np.array(dg)
        front = is_pareto_efficient_simple(costs)
        frontval = [ n if x else 0 for x in front ]
        inframe['fv'] = frontval
        if len( inframe[ (inframe['fv'] > 0) & (inframe['Pareto'] > 0) ] )> 0:
            print('bad')
            break
        #print(n,frontval.count(n))
        inframe['Pareto'] = inframe['Pareto'] + frontval
        inframe.loc[ inframe['Pareto'] > 0,'imprecision'] = 1
        inframe.loc[ inframe['Pareto'] > 0,'unconfidence'] = 1
        n += 1
    return inframe.copy()

