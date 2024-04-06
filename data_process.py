## This script :
# - checks if data is downloaded, with latest version, if not downloads
# - parses the data, pre-processes the datasets
# - combines datasets into one table
# - produces relevant illustrations/graphs

from settings import OPENTARGETS_LINK, DATA_VERSION, DATA_TYPE
import pandas as pd
from utils import convert_to_list, get_loc_values
import tempfile
import os


class DataPreprocess:
    """
    Takes in targets, moa and molecules tsv files,
    Preprocess and combine them into one table/tsv file
    """

    def __init__(self, targets_file, mechanism_of_action_file, molecules_file, output_dir,
                 save_preprocess_data=False, temp_dir=None):

        self.targets_file = targets_file
        self.mechanism_of_action_file = mechanism_of_action_file
        self.molecules_file = molecules_file
        self.output_dir = output_dir
        self.save_preprocess_data = save_preprocess_data
        self.temp_dir = temp_dir if temp_dir is not None else tempfile.mkdtemp(prefix="dataprocess_OT")

        self.preprocessed_moa:pd.DataFrame = None
        self.preprocessed_targets:pd.DataFrame = None
        self.preprocessed_molecules:pd.DataFrame = None
        self.combined_data:pd.DataFrame = None

    def preprocess(self):
        self.get_preprocess_targets()
        self.get_preprocess_moa()
        self.get_preprocess_molecules()
        self.combine_data()

    def get_preprocess_targets(self):
        df_targets = pd.read_csv(self.targets_file, sep="\t")

        ## Simplify the dataset
        ## narrow down the rows with no subcellular data
        df_targets_naless = df_targets.dropna(subset=['subcellularLocations'])

        ## keep useful columns
        columns_to_keep = ["id", "biotype", "alternativeGenes", "subcellularLocations"]
        df_targets = df_targets_naless[columns_to_keep]
        ## handle the subcellularLocations
        # convert string to an array
        df_targets["subcellularLocations"].apply(lambda x: convert_to_list(x), inplace=True)
        df_targets_exp_locs = df_targets.explode("subcellularLocations")
        df_targets_exp_locs.dropna(subset=["subcellularLocations"], inplace=True)

        df_targets_exp_locs[["subcellular_location", "subcellular_location_label"]] = \
        df_targets_exp_locs["subcellularLocations"].apply(lambda x: pd.Series(get_loc_values(x)))

        self.preprocessed_targets = df_targets_exp_locs
        self.preprocessed_targets.to_csv(os.path.join(self.temp_dir, "preprocessed_targets.tsv"))

    def get_preprocess_moa(self):
        df_moa = pd.read_csv(self.mechanism_of_action_file, sep="\t")
        df_moa.drop(columns=["references", "mechanismOfAction", "targetName"], inplace=True)
        df_moa["chemblIds"].apply(lambda x: convert_to_list(x), inplace=True)
        df_moa["targets"].apply(lambda x: convert_to_list(x), inplace=True)
        df_moa_expChemId = df_moa.explode("chemblIds")
        self.preprocessed_moa = df_moa_expChemId.explode("targets")

        self.preprocessed_moa.to_csv(os.path.join(self.temp_dir, "preprocessed_moa.tsv"), sep="\t", index=False)

    def get_preprocess_molecules(self):
        df_molecules = pd.read_csv(self.molecules_file, sep="\t")
        df_molecules = df_molecules[["id", "drugType", "childChemblIds", "parentId", "linkedTargets.rows"]]

        ##since some values are encoded literal strings while transforming from json to pandas,
        # needed to convert string to arrays (lists)
        df_molecules["childChemblIds"].apply(lambda x: convert_to_list(x), inplace=True)
        df_molecules["linkedTargets.rows"].apply(lambda x: convert_to_list(x), inplace=True)

        df_molecules_expChild = df_molecules.explode("childChemblIds")
        self.preprocessed_molecules = df_molecules_expChild.explode("linkedTargets.rows")

        self.preprocessed_molecules.to_csv(os.path.join(self.temp_dir, "preprocessed_molecules.tsv"), sep="\t", index=False)

    def combine_data(self):
        pass
