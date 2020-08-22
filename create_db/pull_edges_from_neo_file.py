import os
import argparse
import json
from neo4j import GraphDatabase
import csv

"""
We  have extracted all the edge from neo4j into a text file that looks like:
"CHEBI:136570","[""named_thing"",""biological_entity"",""chemical_substance"",""molecular_entity""]","subclass_of","CHEBI:33675","[""named_thing"",""biological_entity"",""chemical_substance"",""molecular_entity""]"
"CHEBI:136570","[""named_thing"",""biological_entity"",""chemical_substance"",""molecular_entity""]","subclass_of","CHEBI:30436","[""named_thing"",""biological_entity"",""chemical_substance"",""molecular_entity""]"
"CHEBI:136570","[""named_thing"",""biological_entity"",""chemical_substance"",""molecular_entity""]","subclass_of","CHEBI:33579","[""named_thing"",""biological_entity"",""chemical_substance"",""molecular_entity""]"

Now we want to create a series of files in the data directory like: 
dump.anatomical_entity.anatomical_entity.txt                            dump.chemical_substance.biological_process_or_activity.txt             dump.gene.chemical_substance.txt
dump.anatomical_entity.biological_process_or_activity.txt               dump.chemical_substance.biological_process.txt                         dump.gene.disease_or_phenotypic_feature.txt
dump.anatomical_entity.biological_process.txt                           dump.chemical_substance.chemical_substance.txt                         dump.gene.disease.txt

that each have data looking like:
CHEBI:104017    participates_in SMPDB:SMP0058769        ['named_thing', 'biological_entity', 'chemical_substance', 'molecular_entity']  ['named_thing', 'biological_entity', 'pathway', 'biological_process', 'biological_process_or_activity']
CHEBI:124969    participates_in SMPDB:SMP0000639        ['named_thing', 'biological_entity', 'chemical_substance', 'molecular_entity']  ['named_thing', 'biological_entity', 'pathway', 'biological_process', 'biological_process_or_activity']
CHEBI:125502    participates_in SMPDB:SMP0000422        ['named_thing', 'biological_entity', 'chemical_substance', 'molecular_entity']  ['named_thing', 'biological_entity', 'pathway', 'biological_process', 'biological_process_or_activity']
CHEBI:125502    participates_in SMPDB:SMP0000625        ['named_thing', 'biological_entity', 'chemical_substance', 'molecular_entity']  ['named_thing', 'biological_entity', 'pathway', 'biological_process', 'biological_process_or_activity']
"""

def str2list(nlabels):
    x = nlabels[1:-1] #strip [ ]
    parts = x.split(',')
    labs = [ pi[1:-1] for pi in parts ] #strip ""
    return labs

class ExpansionManagement:
    def __init__(self,filename):
        self.dumpfilename=filename
        #This could be pulled from some combo of the biolink model and the neo4j
        self.types = set(['gene','gene_family','gene_product','chemical_substance','anatomical_entity',
                      'cellular_component','cell','disease','phenotypic_feature','organism_taxon',
                      'disease_or_phenotypic_feature','biological_process','molecular_activity',
                      'biological_process_or_activity','food','pathway','sequence_variant'])

    def dumpdb(self):
        outfiles = {}
        with open(self.dumpfilename,'r') as inf:
            reader = csv.DictReader(inf)
            for line in reader:
                source_id = line['source_id']
                target_id = line['target_id']
                if source_id == '':
                    continue
                pred = line['predicate']
                try:
                    source_labels = str2list(line['source_labels'])
                    target_labels = str2list(line['target_labels'])
                except:
                    print('ERROR:',line)
                    continue
                for slabel in source_labels:
                    if slabel not in self.types:
                        continue
                    if slabel not in outfiles:
                        outfiles[slabel] = {}
                    for tlabel in target_labels:
                        if tlabel not in self.types:
                            continue
                        if tlabel not in outfiles[slabel]:
                            outfiles[slabel][tlabel] = open(f'data/dump.{slabel}.{tlabel}.txt','w')
                        oline = f"{source_id}\t{pred}\t{target_id}\t{source_labels}\t{target_labels}\n"
                        outfiles[slabel][tlabel].write(oline)
        for s,sub in outfiles.items():
            for t,f in sub.items():
                f.close()


def run(args):
    expman = ExpansionManagement(args.database)
    expman.dumpdb()

if __name__ == '__main__':
    #python pull_edges_from_neo.py -d bolt://stars-k5.edc.renci.org:31333 -p XXXXXX -u -e
    parser = argparse.ArgumentParser(description = 'help',
            formatter_class = argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d','--database',help='Path of neo4j dump')
    #parser.add_argument('-s','--source',help = 'type of source node')
    #parser.add_argument('-t','--target',help = 'type of target node')
    #parser.add_argument('-a','--all',help='All combinations of source and target nodes')
    parser.add_argument('-e','--dump',help='DUMP DB',action='store_true')
    args = parser.parse_args()
    run(args)

