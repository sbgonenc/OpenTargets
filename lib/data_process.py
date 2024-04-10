## This script :
# - parses the data, pre-processes the datasets
# - combines datasets into one table
# - produces relevant illustrations/graphs

import pandas as pd
from utils import convert_to_list
import tempfile
import os
import shutil


class DataProcess:
    """
    Takes in targets, moa and molecules json files,
    Preprocess and combine them into one table/tsv file

    """

    def __init__(self, targets_file=None, mechanism_of_action_file=None, molecules_file=None, combined_file=None,
                 drug_modality="drugType", location_key="subcellular_location_label", show_only_significant=False,
                 save_preprocess_data=False, out_dir=None, temp_dir=None):

        self.targets_file = targets_file
        self.mechanism_of_action_file = mechanism_of_action_file
        self.molecules_file = molecules_file
        self.save_preprocess_data = save_preprocess_data
        self.out_dir = out_dir if out_dir is not None else f"./{drug_modality}_analysis"
        self.temp_dir = temp_dir if temp_dir is not None else tempfile.mkdtemp(prefix="dataprocess_OT")
        self.combined_file = combined_file

        self.drug_modality_key = drug_modality
        self.location_key = location_key
        self.show_only_significant = show_only_significant

        self.preprocessed_moa:pd.DataFrame = None
        self.preprocessed_targets:pd.DataFrame = None
        self.preprocessed_molecules:pd.DataFrame = None
        self.combined_data:pd.DataFrame = None

        self.contingency_table = None


    def process(self):
        ## Preprocess the data from json
        ## to combine them into one table
        if self.combined_file is None:
            self.preprocess()
        else:
            self.combined_data = pd.read_csv(self.combined_file, sep="\t")

        ## save preprocessed files to out_dir
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        if self.save_preprocess_data:
            shutil.copy(self.temp_dir, self.out_dir)

        ## remove temp_dir
        shutil.rmtree(self.temp_dir)

        ## Creates contingency table for further analysis
        self.contingency_table = pd.crosstab(self.combined_data[self.location_key], self.combined_data[self.drug_modality_key])
        self.analyse()

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
        self.preprocessed_moa.rename(columns={"chemblIds": "ChemblID", "targets": "EnsemblID"}, inplace=True)
        self.preprocessed_molecules.rename(columns={"id": "ChemblID"}, inplace=True)
        self.preprocessed_targets.rename(columns={"id": "EnsemblID"}, inplace=True)

        ## Merge the datasets
        df_drugmoa = pd.merge(self.preprocessed_moa, self.preprocessed_molecules, on="ChemblID")
        self.combined_data = pd.merge(df_drugmoa, self.preprocessed_targets, on="EnsemblID")

        self.combined_data.to_csv(os.path.join(self.temp_dir, "combined_data.tsv"), sep="\t", index=False)
        del df_drugmoa

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

    @staticmethod
    def _create_contingency_table(df, x, y):
        return pd.crosstab(df[x], df[y])

    def analyse(self):
        """
        Creates a __significance.tsv contains p-value and odds ratio for each drug modality and subcellular location
        and a heatmap for the drug modality and subcellular location
        This method calls test_significance and create_heatmap methods to analyse the data
        drug_modality_key: drug_modality column_name to analyse
        inference_key : subcellular location to analyse
        :return:
        """
        significance_table = ...
        significance_file = os.path.join(self.out_dir, f"{self.drug_modality_key}_{self.location_key}_significance.tsv")
        with open(significance_file, "w") as fh:
            fh.write("Drug Modality\tLocation\tP-value\tOdds Ratio\tSignificance\n")
            for key in self.contingency_table.columns:
                for loc in self.contingency_table.index:
                    fisher_p_value, odds_ratio, significance = self.test_significance(key, loc)
                    if self.show_only_significant and not significance: continue
                    stats_string = f"{fisher_p_value}\t{odds_ratio}\t{significance}"
                    fh.write(f"{key}\t{loc}\t{stats_string}\n")

        self.create_heatmap()
        self.create_stacked_bar_distributions()

    def test_significance(self, column_name, row_name, significance=0.05):
        """
        This function tests the significance of the association between a specific drug type and a subcellular location using Fisher's exact test.

        Args:
          data: cross tab with rows indexed
          column_name: column_name to analyze.
          row_name: row_name location to analyze.

        Returns:
          A tuple containing the p-value and odds ratio from the Fisher's exact test.
        """
        from scipy.stats import fisher_exact, chi2_contingency

        data = self.contingency_table
        # Get contingency table for drug type vs location
        contingency_table = [[0, 0], [0, 0]]
        row_column = data[column_name][row_name]
        not_row_all_column = data[column_name].sum() - row_column
        all_row_not_column = data.loc[row_name].sum() - row_column
        not_row_not_column = data.sum().sum() - not_row_all_column - all_row_not_column + row_column
        contingency_table[0][0] = row_column  ## column+row sum
        contingency_table[1][0] = all_row_not_column  ## row - column
        contingency_table[0][1] = not_row_all_column
        contingency_table[1][1] = not_row_not_column

        # Perform Fisher's exact test
        odds_ratio, fisher_p_value = fisher_exact(contingency_table)
        #chi_stat, chi_p_value = chi2_contingency(contingency_table)
        return fisher_p_value, odds_ratio, significance > fisher_p_value

    def create_heatmap(self, log_transform=True):
        import seaborn as sns
        import numpy as np
        import matplotlib.pyplot as plt

        title = f"{self.drug_modality_key} distribution on subcellular locations"
        contingency_table = self.contingency_table
        if log_transform:
            contingency_table = np.log2(self.contingency_table + 1)
            title = f"{title} (Log Scale)"

        # Create a heatmap using seaborn
        sns.heatmap(contingency_table, annot=False, cmap="viridis")
        plt.title(title)
        plt.xlabel(self.drug_modality_key)
        plt.ylabel("subcellular locations")
        plt.xticks(rotation=45, ha="right")

        plt.savefig(
            os.path.join(self.out_dir, f"{self.drug_modality_key}_{self.location_key}_heatmap.pdf"),
            format="pdf", bbox_inches="tight"
        )
        plt.show()

    def create_stacked_bar_distributions(self):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))  # Adjust figure size as needed
        df_percentage = self._get_percentages("loc")
        df_percentage.plot(kind="bar", stacked=True, use_index=True)
        plt.xlabel("Subcellular Location")
        plt.ylabel("Percentages")
        plt.title(f"Distribution of {self.drug_modality_key} Across Subcellular Locations")
        plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for readability
        plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
        plt.tight_layout()
        plt.savefig(os.path.join(self.out_dir, "stacked_bar_distributions.pdf"), format="pdf", bbox_inches="tight")
        plt.show()

    def _get_percentages(self, location_or_modality="loc"):
        if location_or_modality == "loc": ##percentages by row
            return self.contingency_table.T.apply(lambda x: x * 100 / x.sum()).T
        return self.contingency_table.apply(lambda x: x * 100 / x.sum()) ##precentage by column