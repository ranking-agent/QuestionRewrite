def write_testq(nodelist, predlist, directionlist):
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