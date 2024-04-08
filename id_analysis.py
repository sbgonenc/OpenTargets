# This script looks if different gene IDs from  are intersecting with each other.

def ensembl_id_analysis():
    targets_ids = set()
    alt_gene_ids = set()
    linked_targets = set()
    moa_targets_ids = set() ## dataset to combine CHEMBLIDs and ENSGIDs

    with open("/data/moa_targets_ids.txt", "r") as fh:
        ##cat preprocessed_moa.tsv | cut -f 4 | head -n -1 | sort | uniq -u > moa_targets_ids.txt
        moa_targets_ids.update([ensembl_id.replace("\n", "") for ensembl_id in fh])


    with open("/data/targets_ids.txt", "r") as fh:
        ##cat preprocessed_targets.tsv | cut -f1 | sort | uniq -u | head -n -1 > targets_ids.txt
        targets_ids.update([ensembl_id.replace("\n", "") for ensembl_id in fh])

    with open("/data/alt_genes.txt", "r") as fh:
        ##cat preprocessed_targets.tsv | cut -f3 | sort | uniq -u | head -n -1 > alt_genes.txt
        import re
        ENSG_pattern = r"ENSG\d{11}"
        for line in fh:
            alt_gene_ids.update(re.findall(ENSG_pattern, line))

    with open("/data/mols_linked_ids.txt", "r") as fh:
        ##cat preprocessed_molecules.tsv  | cut -f5 | sort | uniq -u | head -n-1 > mols_linked_ids.txt
        linked_targets.update([ensembl_id.replace("\n", "") for ensembl_id in fh])

    print("MOA Targets")
    print(len(moa_targets_ids))
    # 380

    print("Targets")
    print(len(targets_ids))
    print("Alt Genes")
    print(len(alt_gene_ids))

    print("Linked Targets")
    print(len(linked_targets))

    print("MOA Targets and Targets Intersection:")
    print(len(moa_targets_ids.intersection(targets_ids)))
    # 78
    print(len(moa_targets_ids.difference(targets_ids)))
    #302 difference between moa_targets_ids and targets_ids

    print("MOA Targets and Alt Genes Intersection:")
    print(len(moa_targets_ids.intersection(alt_gene_ids)))
    # 0

    print("MOA Targets and Linked Targets Intersection:")
    print(len(moa_targets_ids.intersection(linked_targets)))
    # 376
    print(linked_targets.issubset(moa_targets_ids))
    # True --> we can ignore linked_targets

    print("Alt Genes and Targets Intersection:")
    print(len(alt_gene_ids.intersection(targets_ids)))
    # 0

    print("Linked Targets and Targets Intersection:")
    print(len(linked_targets.intersection(targets_ids)))

    print("Linked Targets and Alt Genes Intersection:")
    print(len(linked_targets.intersection(alt_gene_ids)))
    # 0

    print("Linked Targets but not in Targets:")
    print(len(linked_targets.difference(targets_ids)))

    print("Linked Targets but not in Alt Genes:")
    print(len(linked_targets.difference(alt_gene_ids)))

    ## Intersections with Alt Genes are 0, so we can ignore them.


def chembl_id_analysis():
    ## Let's look at the Chembl Ids
    moa_chembl_ids = set()
    molecules_chembl_ids = set()
    molecules_parents = set()
    molecules_children = set()

    with open("/home/berk/Projects/OpenTargets/moa_chembl_ids.txt", "r") as fh:
        #cat preprocessed_moa.tsv | cut -f 2 | head -n -1 | sort | uniq -u > moa_chembl_ids.txt
        moa_chembl_ids.update([chembl_id.replace("\n", "") for chembl_id in fh])

    with open("/home/berk/Projects/OpenTargets/preprocessed_molecules.tsv", "r") as fh:
        for line in fh:
            line = line.split("\t")
            molecules_chembl_ids.add(line[0])
            molecules_parents.add(line[3])
            molecules_children.add(line[2])

        molecules_parents.remove("")
        molecules_children.remove("")


    print("MOA Chembl Ids")
    print(len(moa_chembl_ids))

    print("Molecules Chembl Ids")
    print(len(molecules_chembl_ids))

    print("Molecules Parents")
    print(len(molecules_parents))

    print("Molecules Children")
    print(len(molecules_children))

    print("Is parents and children subset of molecule ids?")
    print(molecules_parents.issubset(molecules_chembl_ids)) ## False
    print(molecules_children.issubset(molecules_chembl_ids)) ## False

    print("PUC/molecules_chembl_ids n moa_chembl_ids")
    print(molecules_parents.union(molecules_children).difference(molecules_chembl_ids).intersection(moa_chembl_ids))

    print("MOA Chembl Ids and Molecules Chembl Ids Intersection:")
    print(len(moa_chembl_ids.intersection(molecules_chembl_ids)))
    ## 3515

    print("MOA Chembl Ids and Molecules Parents Intersection:")
    print(len(moa_chembl_ids.intersection(molecules_parents)))
    ## 431

    print("MOA Chembl Ids and Molecules Children Intersection:")
    print(len(moa_chembl_ids.intersection(molecules_children)))
    ## 538

    print("MOA Chembl Ids in Parents and Children but not in molecules:")
    print(len(moa_chembl_ids.intersection(molecules_parents.union(molecules_children)).difference(molecules_chembl_ids)))
    ## 0

    ## When ID matching, we do not need to take into account parents and children.
    print(molecules_parents.intersection(moa_chembl_ids))

    print(molecules_parents.intersection(molecules_chembl_ids))


chembl_id_analysis()
