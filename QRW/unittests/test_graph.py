import pytest

import QRW.graph_util
from QRW.unittests.common import write_testq

def test_get_node():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    node = QRW.graph_util.get_node(tq, 'node_1')
    assert node['id'] == 'node_1'
    assert QRW.graph_util.get_node(tq, 'bad_node') is None

def test_get_edge():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    edge = QRW.graph_util.get_edge(tq, 'edge_1')
    assert edge['type'] == 'contributes_to'
    assert QRW.graph_util.get_edge(tq, 'bad_node') is None

def test_get_source_and_target_type():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_transport_of', 'contributes_to'],
                     [True, True])
    stype0 = QRW.graph_util.get_source_type(tq, 'edge_0')
    stype1 = QRW.graph_util.get_source_type(tq, 'edge_1')
    assert stype0 == 'gene'
    assert stype1 == 'chemical_substance'
    ttype0 = QRW.graph_util.get_target_type(tq, 'edge_0')
    ttype1 = QRW.graph_util.get_target_type(tq, 'edge_1')
    assert ttype0 == 'chemical_substance'
    assert ttype1 == 'disease'

def test_get_source_and_target_type_flipped():
    tq = write_testq(['gene', 'chemical_substance', 'disease'],
                     ['increases_expression_of', 'contributes_to'],
                     [False, True])
    stype0 = QRW.graph_util.get_source_type(tq, 'edge_0')
    stype1 = QRW.graph_util.get_source_type(tq, 'edge_1')
    assert stype0 == 'chemical_substance'
    assert stype1 == 'chemical_substance'
    ttype0 = QRW.graph_util.get_target_type(tq, 'edge_0')
    ttype1 = QRW.graph_util.get_target_type(tq, 'edge_1')
    assert ttype0 == 'gene'
    assert ttype1 == 'disease'

