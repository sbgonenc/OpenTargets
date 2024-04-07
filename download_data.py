import os
from settings import OPENTARGETS_LINK, DATA_VERSION, DATA_TYPE
from utils import call_subprocess
import tempfile


class DownloadPrepareInitialData:
    """
    Downloads the OpenTargets dataset and joins the json files
    """

    def __init__(self, mechanism_of_action_output=None, targets_output=None, molecules_output=None,  temp_dir=None):

        self.temp_dir = temp_dir if temp_dir is not None else tempfile.mkdtemp(prefix="download_OT")

        print(self.temp_dir)

        self.moa_combined = mechanism_of_action_output if mechanism_of_action_output is not None else os.path.join(self.temp_dir, "moa_combined.json")
        self.targets_combined = targets_output if targets_output is not None else os.path.join(self.temp_dir, "targets_combined.json")
        self.molecules_combined = molecules_output if molecules_output is not None else os.path.join(self.temp_dir, "molecules_combined.json")

    def process(self):
        self.download_data("targets")
        self.join_json_files(os.path.join(self.temp_dir, "targets"), self.targets_combined)

        self.download_data("mechanismOfAction")
        self.join_json_files(os.path.join(self.temp_dir, "mechanismOfAction"), self.moa_combined)

        self.download_data("molecule")
        self.join_json_files(os.path.join(self.temp_dir, "molecule"), self.molecules_combined)


    def download_data(self, data_name):
        """
        Downloads the OpenTargets dataset from the link specified in settings.py
        """

        download_url = f"{OPENTARGETS_LINK}/{DATA_VERSION}/output/etl/{DATA_TYPE}/{data_name}"

        download_params = ["--recursive", "--no-parent", "--no-host-directories", "--cut-dirs", "8", "--directory-prefix", self.temp_dir,  download_url]

        return_code, _ = call_subprocess("wget", download_params)

        if return_code != 0:
            raise Exception("Download failed")

        print(f"Downloaded {data_name}")
        return 1

    def join_json_files(self, input_folder, output_file):
        """
        Joins all the json lines files in the input_folder into one file
        """
        return_code, _ = call_subprocess("cat", [f"{input_folder}/*.json"], outfile=output_file)

        if return_code != 0:
            raise Exception("Joining failed")
        return 1