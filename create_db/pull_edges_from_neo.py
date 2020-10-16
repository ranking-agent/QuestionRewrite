import os
import argparse
import json
from neo4j import GraphDatabase

"""
We want to build a list of good expansions of edges.
Specifically, given a query (A)-[x]-(B) where A and B are semantic types and x is a specific predicate,
we want to find expanded queries of the form (A)-[p]-(C)-[q]-(B) with which [x] may be replaced.

To do this we are going to
1) Get the counts of every (A)-[x]-(B) query.
2) For each (A,x,B), get counts of (A)-[x]-(B)-[q]-(C)-[p]-(A), as well as (A)-[p]-(C)-[q]-(B).
2a) the latter query should be cached and reused.
3) Calculate sensitivity/specificity [for each direction], as well as overall correlation.
"""

class ExpansionManagement:
    def __init__(self,db_url,neo4j_password):
        self.ddir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data')
        self._driver = self.driver(db_url,neo4j_password)
        #Make sure it worked...
        res = self.query('match (a:gene {id:"NCBIGene:445"}) return a')
        if len(res) != 1:
            print('Connection to neo4j failed')
            exit()
        #This could be pulled from some combo of the biolink model and the neo4j
        #self.types = ['gene','gene_family','gene_product','chemical_substance','anatomical_entity',
        #              'cellular_component','cell','disease','phenotypic_feature','organism_taxon',
        #              'disease_or_phenotypic_feature','biological_process','molecular_activity',
        #              'biological_process_or_activity','food','pathway','sequence_variant']
        self.types = ['gene', 'sequence_variant']
        self.one_hops = self.read_one_hops()


    def driver(self,url,neo4j_password):
        auth=("neo4j", neo4j_password)
        return GraphDatabase.driver(url, auth=auth)

    def query(self,cypher):
        with self._driver.session() as session:
            results = session.run(cypher)
            data = results.data()
        return data

    def dumpdb(self):
        for source in self.types:
            for target in self.types:
                q = f'''MATCH (a:{source})-[x]->(b:{target}) 
                       WHERE NOT a:Concept
                       AND NOT b:Concept
                       RETURN DISTINCT a.id as a,type(x) as x,
                              b.id as b,labels(a) as la,labels(b) as lb
                        '''
                data = self.query(q)
                if len(data) > 0:
                    with open(f'data/dump.{source}.{target}.txt','w') as outf:
                        for d in data:
                            outf.write(f"{d['a']}\t{d['x']}\t{d['b']}\t{d['la']}\t{d['lb']}\n")

    def update_one_hops(self):
        results = []
        for t in self.types:
            for s in self.types:
                q= f'''MATCH (a:{t})-[x]->(b:{s}) 
                   WHERE NOT a:Concept and NOT b:Concept 
                   RETURN "{t}" AS sourcelabel, type(x) AS edgetype, "{s}" AS targetlabel, COUNT(*) as count'''
                results += self.query(q)
        self.write_one_hops(results)
        self.one_hops = results

    def write_one_hops(self,results):
        if not os.path.exists(self.ddir):
            os.makedirs(self.ddir)
        with open(os.path.join(self.ddir,'onehop.json'),'w') as outf:
            json.dump(results,outf,indent=4)

    def read_one_hops(self):
        infname = os.path.join(self.ddir,'onehop.json')
        if not os.path.exists(infname):
            return None
        with open(infname,'r') as inf:
            results = json.load(inf)
        return results

    def perform_single_pair(self,sourcetype,targettype):
        shortlist=[]
        for result in self.one_hops:
            if result['sourcelabel'] == sourcetype and result['targetlabel'] == targettype:
                shortlist.append(result)
        for result in shortlist:
            self.perform_pair_with_edge(sourcetype,targettype,result['edgetype'],result['count'])

    def perform_pair_with_edge(self,sourcetype,targettype,edgetype,count):
        print(sourcetype,targettype,edgetype,count)
        left = f'''(a)-[x]->(c)'''
        qbasic = f'''MATCH (a:{sourcetype})-[:{edgetype}]-(b:{targettype})'''



def run(args):
    expman = ExpansionManagement(args.database, args.password)
    if args.dump:
        print('dumpit')
        expman.dumpdb()
        exit()
    if args.update1hops:
        expman.update_one_hops()
    if args.target is not None and args.source is not None:
        expman.perform_single_pair(args.source,args.target)

if __name__ == '__main__':
    #python pull_edges_from_neo.py -d bolt://stars-k5.edc.renci.org:31333 -p XXXXXX -u -e
    parser = argparse.ArgumentParser(description = 'help',
            formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d','--database',help='URL of neo4j')
    parser.add_argument('-p','--password',help='password for neo4j')
    parser.add_argument('-u','--update1hops',help = 'Update database of 1-hops',action = 'store_true')
    parser.add_argument('-s','--source',help = 'type of source node')
    parser.add_argument('-t','--target',help = 'type of target node')
    parser.add_argument('-a','--all',help='All combinations of source and target nodes')
    parser.add_argument('-e','--dump',help='DUMP DB',action='store_true')
    args = parser.parse_args()
    run(args)

