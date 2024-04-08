## This script :
# - parses the data, pre-processes the datasets
# - combines datasets into one table
# - produces relevant illustrations/graphs

import pandas as pd
from utils import convert_to_list
import tempfile
import os


class DataPreprocess:
    """
    Takes in targets, moa and molecules json files,
    Preprocess and combine them into one table/tsv file
    """

    def __init__(self, targets_file, mechanism_of_action_file, molecules_file,
                 save_preprocess_data=False, temp_dir=None):

        self.targets_file = targets_file
        self.mechanism_of_action_file = mechanism_of_action_file
        self.molecules_file = molecules_file
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
        df_targets = self._read_json_data(self.targets_file)

        ## Simplify the dataset
        ## narrow down the rows with no subcellular data
        df_targets.dropna(subset=['subcellularLocations'], inplace=True)

        ## keep useful columns
        columns_to_keep = ["id", "biotype", "subcellularLocations"]
        df_targets = df_targets[columns_to_keep]
        ## handle the subcellularLocations
        # convert string to an array
        df_targets["subcellularLocations"] = df_targets["subcellularLocations"].apply(lambda x: convert_to_list(x))
        df_targets_exp_locs = df_targets.explode("subcellularLocations")
        df_targets_exp_locs.dropna(subset=["subcellularLocations"], inplace=True)

        df_targets_exp_locs[["subcellular_location", "subcellular_location_label"]] = df_targets_exp_locs["subcellularLocations"].apply(lambda x: pd.Series(self._get_target_loc_values(x)))

        self.preprocessed_targets = df_targets_exp_locs.drop("subcellularLocations", axis=1)
        self.preprocessed_targets.to_csv(os.path.join(self.temp_dir, "preprocessed_targets.tsv"), sep="\t", index=False)
        ### Free memory
        del df_targets
        del df_targets_exp_locs

    def get_preprocess_moa(self):
        df_moa = self._read_json_data(self.mechanism_of_action_file)
        df_moa.drop(columns=["references", "mechanismOfAction", "targetName"], inplace=True)
        df_moa["chemblIds"] = df_moa["chemblIds"].apply(lambda x: convert_to_list(x))
        df_moa["targets"] = df_moa["targets"].apply(lambda x: convert_to_list(x))
        df_moa_expChemId = df_moa.explode("chemblIds")
        self.preprocessed_moa = df_moa_expChemId.explode("targets")
        self.preprocessed_moa.dropna(subset=["targets"], inplace=True)
        self.preprocessed_moa.to_csv(os.path.join(self.temp_dir, "preprocessed_moa.tsv"), sep="\t", index=False)
        ## Free memory
        del df_moa
        del df_moa_expChemId

    def get_preprocess_molecules(self):
        df_molecules = self._read_json_data(self.molecules_file)
        self.preprocessed_molecules = df_molecules[["id", "drugType"]]

        self.preprocessed_molecules.to_csv(os.path.join(self.temp_dir, "preprocessed_molecules.tsv"), sep="\t", index=False)
        ## Free memory
        del df_molecules

    def combine_data(self):
        pass

    @staticmethod
    def _read_json_data(json_file):
        "Reads json file, normalizes and returns pandas dataframe"
        from utils import convert_json2pandas
        return convert_json2pandas(json_file)

    @staticmethod
    def _get_target_loc_values(x):
        location = x.get("location", None)
        if ":" in location: location = location.split(":")[1].strip()
        return location, x.get("labelSL", None)
