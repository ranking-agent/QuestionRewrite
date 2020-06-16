import os
import ast

def parse_files(files):
    triples = set()
    types = {}
    newpreds = set()
    with open('predicates','w') as predicatefile, open('instances','w') as instancefile:
        for f in files:
            print(f)
            if f.startswith('dump'):
                parts = f.split('.')
                source = parts[1]
                target = parts[2]
                with open(f"data/{f}",'r') as inf:
                    for line in inf:
                        x = line.split('\t')
                        subject=x[0]
                        object=x[2]
                        if subject == object:
                            continue
                        pred = x[1]
                        slabels=ast.literal_eval(x[3])
                        olabels=ast.literal_eval(x[4])
                        triple = (subject,pred,object)
                        if triple not in triples:
                            triples.add(triple)
                            subject_type = get_type(subject,slabels,types)
                            object_type = get_type(object,olabels,types)
                            newpred = get_pred(pred,subject_type,object_type,newpreds,predicatefile)
                            if newpred is not None:
                                instancefile.write(f'<{subject}>\t<{newpred}>\t<{object}>\n')

def get_type(instance,labels,typemap):
    if instance in typemap:
        return typemap[instance]
    typeorder=['cell','cellular_component','anatomical_entity','disease','phenotypic_feature','disease_or_phenotypic_feature','biological_process_or_activity','gene','gene_product','gene_family','biological_process_or_activity','chemical_substance','food','sequence_variant','organism_taxon']
    for t in typeorder:
        if t in labels:
            rtype = t
            typemap[instance]=t
            return t
    print(labels)
    exit()

def get_pred(inpred,stype,otype,preds,pfile):
    if inpred == 'Unmapped_Relation':
        return None
    newpred = f'{stype}__{inpred}__{otype}'
    if newpred not in preds:
        pfile.write(f'<{newpred}>\t<http://www.w3.org/2000/01/rdf-schema#domain>\t<{stype}>\n')
        pfile.write(f'<{newpred}>\t<http://www.w3.org/2000/01/rdf-schema#range>\t<{otype}>\n')
        preds.add(newpred)
    return newpred

def go():
    files = os.listdir('data')
    parse_files(files)

if __name__ == '__main__':
    go()