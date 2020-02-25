import numpy
import pandas as pd
from collections import defaultdict
import src.edge_expand_rewrite as rw
from src.graph_util import print_linear_graph

def write_testq(nodelist,predlist,directionlist):
    querygraph = {}
    nodes = []
    edges = []
    for i,nt in enumerate(nodelist):
        nodes.append( {'id': f'node_{i}', 'type':nt} )
    for i,p in enumerate(predlist):
        if directionlist[i]:
            edges.append( {'id': f'edge_{i}', 'type': p, 'source_id': f'node_{i}', 'target_id': f'node_{i+1}'})
        else:
            edges.append( {'id': f'edge_{i}', 'type': p, 'source_id': f'node_{i+1}', 'target_id': f'node_{i}'})

    querygraph["machine_question"] = {'nodes': nodes}
    querygraph["machine_question"].update({'edges': edges})
    querygraph['name'] = ''
    querygraph['natural_question'] = ''
    querygraph['notes'] = ''

    return querygraph

def test_simple_exp():
    tq = write_testq(['chemical_substance','disease'], ['treats'], [True])
    print( print_linear_graph(tq))
    nqs = rw.rewrite_edge_expand(tq)
    #I should get back at least a few new questions, and they should each have 3 nodes and 2 edges and go
    # chemical-[x]-(?)-[y]-disease
    assert len(nqs) > 3
    for nq in nqs:
        print( print_linear_graph(nq))
        assert len(nq['nodes']) == 3
        assert len(nq['edges']) == 2

def test_depth2_exp():
    tq = write_testq(['chemical_substance','disease'], ['treats'], [True])

    if tq.get('machine_question') is not None:
        tq = tq['machine_question']

    original_node_ids =  [node['id'] for node in tq['nodes']]
    nq_1 = rw.rewrite_edge_expand(tq)
    nq_2 = rw.rewrite_edge_expand(tq,depth=2)
    #I should get more back in depth 2 than depth 1
    assert len(nq_2) > len(nq_1)
    #depth =1 should be a proper subset of depth = 2
    strings_1 = set([ print_linear_graph(q) for q in nq_1])
    strings_2 = set([ print_linear_graph(q) for q in nq_2])
    assert strings_1.issubset(strings_2)
    #For every answer, our original nodes should still be the terminal nodes
    #But what does terminal node mean?  It doesn't mean that there's only one edge.
    # Because you can replace a->b with a pair of replacements.
    # It does mean that each should only be attached to a single other node (even if
    # it happens via multiple edges)
    for q in nq_2:
        adjacency = defaultdict(set)
        for edge in q['edges']:
            adjacency[edge['source_id']].add(edge['target_id'])
            adjacency[edge['target_id']].add(edge['source_id'])
        for tnode in original_node_ids:
            assert len(adjacency[tnode]) == 1


def test_edge_expand():
    tq = write_testq(['chemical_substance','disease'], ['treats'], [True])

    if tq.get('machine_question') is not None:
        tq = tq['machine_question']

    #amie_v1 isn't usually exposed, this is just for the test.
    nqs = rw.edge_expand(tq,'edge_0','amie_v1.db')
    assert len(nqs) > 3
    for nq in nqs:
        #This isn't guaranteed, because some of these will not always replace one edge with two.
        #Sometimes it will just replace the predicate
        #But for treats and amie_v1, it is true.
        assert len(nq['nodes']) == 3
        assert len(nq['edges']) == 2

def test_edge_lookup():
    #Maybe replace with a test db?
    expander = 'amie_v1.db'
    source_type = 'chemical_substance'
    edge_type='treats'
    target_type='disease'
    #Returns a pandas data frame
    rs = rw.lookup_edge_expansions(expander, source_type, edge_type, target_type)
    assert len(rs) > 50
    assert 'expansions' in list(rs.columns)

def test_add_pareto():
    xp = numpy.linspace(1,0,10)
    #Pareto surface 1
    yp = 1-xp
    #Pareto surface 2
    yp2 = yp-0.2
    #Pareto surface 3
    yp3 = yp-0.5
    x = numpy.concatenate([xp,xp,xp])
    y = numpy.concatenate([yp,yp2,yp3])
    df = pd.DataFrame( {'headcoverage':x, 'pcaconfidence':y })
    df2 = df [ df['pcaconfidence'] >= 0].copy()
    assert len(df2) == 23
    dfp = rw.add_pareto_values(df2)
    assert len(dfp) == len(df2)
    assert len(dfp[dfp['Pareto'] == 1]) == 10
    assert len(dfp[dfp['Pareto'] == 2]) == 8
    assert len(dfp[dfp['Pareto'] == 3]) == 5

def test_replace_edge():
    """Test replacement of one edge with a different predicate"""
    tq = write_testq(['chemical_substance','disease'], ['treats'], [True])

    if tq.get('machine_question') is not None:
        tq = tq['machine_question']

    replace_edge = 'edge_0'
    expansion = {'nodes':[{'id':'a', 'type': 'chemical_subtance'},
                          {'id':'b', 'type': 'disease'}],
                 'edges':[ {'id': 'x', 'type': 'related_to', 'source_id':'a',
                            'target_id': 'b'}
                          ]}
    rw.replace_edge(tq,replace_edge,expansion)
    assert len(tq['nodes']) == 2
    assert len(tq['edges']) == 1
    assert tq['edges'][0]['type'] == 'related_to'
    assert tq['edges'][0]['source_id'] == 'node_0'
    assert tq['edges'][0]['target_id'] == 'node_1'


def test_replace_edge_reverse():
    """Test replacement of one edge with a different predicate pointing the othe way"""
    tq = write_testq(['chemical_substance', 'disease'], ['treats'], [True])

    if tq.get('machine_question') is not None:
        tq = tq['machine_question']

    replace_edge = 'edge_0'
    expansion = {'nodes': [{'id': 'a', 'type': 'chemical_subtance'},
                           {'id': 'b', 'type': 'disease'}],
                 'edges': [{'id': 'x', 'type': 'related_to', 'source_id': 'b',
                            'target_id': 'a'}
                           ]}
    rw.replace_edge(tq, replace_edge, expansion)
    assert len(tq['nodes']) == 2
    assert len(tq['edges']) == 1
    assert tq['edges'][0]['type'] == 'related_to'
    assert tq['edges'][0]['source_id'] == 'node_1'
    assert tq['edges'][0]['target_id'] == 'node_0'

def test_replace_one_edge_with_two():
    """Test replacement of one edge with a different predicate pointing the othe way"""
    tq = write_testq(['chemical_substance', 'disease'], ['treats'], [True])

    if tq.get('machine_question') is not None:
        tq = tq['machine_question']

    replace_edge = 'edge_0'
    expansion = {'nodes': [{'id': 'a', 'type': 'chemical_substance'},
                           {'id': 'c', 'type': 'gene'},
                           {'id': 'b', 'type': 'disease'}],
                 'edges': [{'id': 'y', 'type': 'disease_to_gene', 'source_id': 'b',
                            'target_id': 'c'},
                           {'id': 'x', 'type': 'reduces_activity_of', 'source_id': 'a',
                            'target_id': 'c'}
                           ]}
    rw.replace_edge(tq, replace_edge, expansion)
    print( node['id'] for node in tq['nodes'])
    #Did we end up with the right number of things?
    assert len(tq['nodes']) == 3
    assert len(tq['edges']) == 2
    #Check ids are unique
    assert len( set([n['id'] for n in tq['nodes']]) ) == len(tq['nodes'])
    assert len( set([n['id'] for n in tq['edges']]) ) == len(tq['edges'])
    #Is everything hooked together properly (mainly checking that id's are modified
    # correctly
    foundone=False
    foundtwo=False
    for edge in tq['edges']:
        if edge['type'] == 'reduces_activity_of':
            foundone = True
            assert edge['source_id'] == 'node_0'
        elif edge['type'] == 'disease_to_gene':
            foundtwo = True
            assert edge['source_id'] == 'node_1'
    assert (foundone and foundtwo)
    assert tq['edges'][0]['target_id'] == tq['edges'][1]['target_id']

def test_replace_one_edge_with_two_twice():
    """Test replacement of one edge with a different predicate pointing the othe way"""
    tq = write_testq(['chemical_substance', 'disease'], ['treats'], [True])

    if tq.get('machine_question') is not None:
        tq = tq['machine_question']

    replace_edge = 'edge_0'
    expansion = {'nodes': [{'id': 'a', 'type': 'chemical_substance'},
                           {'id': 'c', 'type': 'gene'},
                           {'id': 'b', 'type': 'disease'}],
                 'edges': [{'id': 'y', 'type': 'disease_to_gene', 'source_id': 'b',
                            'target_id': 'c'},
                           {'id': 'x', 'type': 'reduces_activity_of', 'source_id': 'a',
                            'target_id': 'c'}
                           ]}
    rw.replace_edge(tq, replace_edge, expansion)
    #find a new replace edge
    for edge in tq['edges']:
        if edge['type'] == 'disease_to_gene':
            e2 = edge['id']
    expansion2 = {'nodes': [{'id': 'a', 'type': 'gene'},
                           {'id': 'c', 'type': 'phenotypic_feature'},
                           {'id': 'b', 'type': 'disease'}],
                 'edges': [{'id': 'y', 'type': 'phenotype_to_gene', 'source_id': 'c',
                            'target_id': 'a'},
                           {'id': 'x', 'type': 'has_phenotype', 'source_id': 'b',
                            'target_id': 'c'}
                           ]}
    rw.replace_edge(tq, e2, expansion2)
    #Now, we should have 4 nodes, and 3 edges.
    assert len(tq['nodes']) == 4
    assert len(tq['edges']) == 3
    #Check ids are unique
    assert len( set([n['id'] for n in tq['nodes']]) ) == len(tq['nodes'])
    assert len( set([n['id'] for n in tq['edges']]) ) == len(tq['edges'])

