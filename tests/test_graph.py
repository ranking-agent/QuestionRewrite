import src.graph_util
from .common import write_testq

def test_get_node():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    node = src.graph_util.get_node(tq, 'node_1')
    assert node['id'] == 'node_1'
    assert src.graph_util.get_node(tq, 'bad_node') is None

def test_get_edge():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    edge = src.graph_util.get_edge(tq, 'edge_1')
    assert edge['type'] == 'contributes_to'
    assert src.graph_util.get_edge(tq, 'bad_node') is None

def test_get_source_and_target_type():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    stype0 = src.graph_util.get_source_type(tq, 'edge_0')
    stype1 = src.graph_util.get_source_type(tq, 'edge_1')
    assert stype0 == 'gene'
    assert stype1 == 'chemical_substance'
    ttype0 = src.graph_util.get_target_type(tq, 'edge_0')
    ttype1 = src.graph_util.get_target_type(tq, 'edge_1')
    assert ttype0 == 'chemical_substance'
    assert ttype1 == 'disease'

def test_get_source_and_target_type_flipped():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_expression_of', 'contributes_to'],
                     [False, True])
    stype0 = src.graph_util.get_source_type(tq, 'edge_0')
    stype1 = src.graph_util.get_source_type(tq, 'edge_1')
    assert stype0 == 'chemical_substance'
    assert stype1 == 'chemical_substance'
    ttype0 = src.graph_util.get_target_type(tq, 'edge_0')
    ttype1 = src.graph_util.get_target_type(tq, 'edge_1')
    assert ttype0 == 'gene'
    assert ttype1 == 'disease'

def test_remove_edge():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                 ['increases_expression_of', 'contributes_to'],
                 [False, True])
    e = src.graph_util.remove_edge(tq,'edge_1')
    assert e['type'] == 'contributes_to'
    assert e['source_id'] == 'node_1'
    assert len(tq['edges']) == 1


