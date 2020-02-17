import pytest
import QRW.rewrite as rw
from collections import defaultdict

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
    querygraph['nodes'] = nodes
    querygraph['edges'] = edges
    return querygraph

def test_simple_sim():
    tq = write_testq(['gene','chemical_substance','disease'],
                     ['increases_transport_of','contributes_to'],
                     [True,True])
    print(tq)
    nqs = rw.similarity_expand(tq)
    assert len(nqs) == 1
    assert len(nqs[0]['nodes']) == 4

def test_shortest_sim():
    tq = write_testq(['gene','chemical_substance'],
                     ['increases_transport_of'],
                     [True])
    print(tq)
    nqs = rw.similarity_expand(tq)
    assert len(nqs) == 1
    assert len(nqs[0]['nodes']) == 3

def test_double_sim():
    tq = write_testq(['gene', 'chemical_substance', 'disease','chemical_substance'],
                     ['increases_transport_of', 'contributes_to', 'treats'],
                     [True, True, False])
    newqueries = rw.similarity_expand(tq)
    assert len(newqueries) == 3
    counts = defaultdict(int)
    for nq in newqueries:
        counts[ (len(nq['nodes']), len(nq['edges']))] += 1
    print(counts)
    #There should be 2 cases where we added one node and 1 case where we added 2
    assert counts[(5,4)] == 2
    assert counts[(6,5)] == 1


def test_node_expansion_linear():
    tq = write_testq(['gene','chemical_substance','disease'],
                     ['increases_transport_of','contributes_to'],
                     [True,True])
    enode = 'node_1'
    newqueries = rw.apply_node_expansion(tq,enode)
    assert len(newqueries) == 1
    nq = newqueries[0]
    assert len(nq['nodes']) == 4
    assert len(nq['edges']) == 3
    #More detailed testing of the query in test_edge_part_of_node_expansion

def test_node_expansion_end():
    tq = write_testq(['gene', 'disease', 'chemical_substance'],
                     ['gene_to_disease', 'contributes_to'],
                     [True, False])
    enode = 'node_2'
    newqueries = rw.apply_node_expansion(tq, enode)
    assert len(newqueries) == 1
    nq = newqueries[0]
    assert len(nq['nodes']) == 4
    assert len(nq['edges']) == 3
    # More detailed testing of the query in test_edge_part_of_node_expansion

def test_node_expansion_branch():
    """Test expanding the pivot of a Y pattern."""
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    node3 = {"id": "node_3", "type": 'gene'}
    edge2 = {"id": "edge_2", "type": 'decreases_transport_of', "source_id": "node_3", "target_id": "node_1"}
    tq['nodes'].append(node3)
    tq['edges'].append(edge2)
    enode = 'node_1'
    newqueries = rw.apply_node_expansion(tq, enode)
    assert len(newqueries) == 3
    counts = defaultdict(int)
    for nq in newqueries:
        counts[ (len(nq['nodes']), len(nq['edges']))] += 1
    print(counts)
    #There should be 2 cases where we added one node and 1 case where we added 2
    assert counts[(5,4)] == 2
    assert counts[(6,5)] == 1

def test_edge_part_of_node_expansion():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    enode = 'node_1'
    eedge = 'edge_1'
    nq = rw.apply_node_expansion_along_edge(tq, eedge, enode)
    #did we add a node?
    assert len(nq['nodes']) == 4
    #are the node ids all unique?
    assert len(set([n['id'] for n in nq['nodes']])) == 4
    #Did we add an edge?
    assert len(nq['edges']) == 3
    #are the edge ids all unique?
    assert len(set([n['id'] for n in nq['edges']])) == 3
    #But we don't want to have changed tq
    assert len(tq['nodes']) == 3
    assert len(tq['edges']) == 2
    #Check the topology of the new query
    degree = defaultdict(int)
    for e in nq['edges']:
        degree[e['source_id']] += 1
        degree[e['target_id']] += 1
    assert degree['node_0'] == 1
    assert degree['node_1'] == 2
    assert degree['node_2'] == 1
    newnodeid = nq['nodes'][-1]['id']
    assert newnodeid not in ['node_0','node_1','node_2']
    assert degree[newnodeid] == 2

def test_get_node():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    node = rw.get_node(tq,'node_1')
    assert node['id'] == 'node_1'
    assert rw.get_node(tq,'bad_node') is None

def test_add_sim_node():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    rw.add_sim_node('node_1',tq)
    #Now there are 4 nodes
    assert len(tq['nodes']) == 4
    #There are still only 2 edges
    assert len(tq['edges']) == 2
    #There need to be 4 unique node identifiers
    nodeids = set( [n['id'] for n in tq['nodes']])
    assert len(nodeids) == 4

def test_generate_novel_sim_id():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    nid = rw.generate_novel_sim_id('node_0',tq)
    original_node_ids = [node['id'] for node in tq['nodes']]
    assert nid not in original_node_ids
    tq['nodes'].append( {'id':nid} )
    nid2 = rw.generate_novel_sim_id('node_0',tq)
    assert nid2 != nid
    original_node_ids2 = [node['id'] for node in tq['nodes']]
    assert nid2 not in original_node_ids2



