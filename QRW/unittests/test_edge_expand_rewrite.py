import pytest
import QRW.edge_expand_rewrite as rw
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

def test_simple_exp():
    tq = write_testq(['chemical_substance','disease'], ['treats'], [True])
    print(tq)
    nqs = rw.rewrite_edge_expand(tq)
    #I should get back at least a few new questions, and they should each have 3 nodes and 2 edges and go
    # chemical-[x]-(?)-[y]-disease
    assert len(nqs) > 3
    for nq in nqs:
        assert len(nq['nodes']) == 3
        assert len(nq['edges']) == 2

def test_edge_expand():
    tq = write_testq(['chemical_substance','disease'], ['treats'], [True])
    #amie_v1 isn't usually exposed, this is just for the test.
    nqs = rw.edge_expand(tq,'edge_0','amie_v1')
    assert len(nqs) > 3
    for nq in nqs:
        assert len(nq['nodes']) == 3
        assert len(nq['edges']) == 2
