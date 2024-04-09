import os
from settings import OPENTARGETS_LINK, DATA_VERSION, DATA_TYPE
from utils import call_subprocess
import tempfile


class DownloadPrepareInitialData:
    """
    Downloads the OpenTargets dataset and joins the json files.
    If the output files are not specified, it creates them in a temporary directory
    If download is set to False, work_dir should be specified as the directory containing the downloaded directories
    """

    def __init__(self, mechanism_of_action_output=None, targets_output=None, molecules_output=None,  work_dir=None):

        self.temp_dir = work_dir if work_dir is not None else tempfile.mkdtemp(prefix="download_OT")
        self.moa_combined = mechanism_of_action_output if mechanism_of_action_output is not None else tempfile.mktemp(dir=self.temp_dir, suffix="moa_combined.json")
        self.targets_combined = targets_output if targets_output is not None else tempfile.mktemp(dir=self.temp_dir, suffix="targets_combined.json")
        self.molecules_combined = molecules_output if molecules_output is not None else tempfile.mktemp(dir=self.temp_dir, suffix="molecules_combined.json")

    def process(self, download=True):
        if download:
            print(f"Downloading targets to {os.path.join(self.temp_dir, 'targets')}")
            self.download_data("targets")
            print(f"Downloading mechanismOfAction to {os.path.join(self.temp_dir, 'mechanismOfAction')}")
            self.download_data("mechanismOfAction")
            print(f"Downloading molecule to {os.path.join(self.temp_dir, 'molecule')}")
            self.download_data("molecule")

        self.join_json_files(os.path.join(self.temp_dir, "targets"), self.targets_combined)
        self.join_json_files(os.path.join(self.temp_dir, "mechanismOfAction"), self.moa_combined)
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

    @staticmethod
    def join_json_files(input_folder, output_file):
        """
        Joins all the json lines files in the input_folder into one file
        """
        with open(output_file, "w") as out_fh:
            for file in os.listdir(input_folder):
                if not file.endswith(".json"): continue
                with open(os.path.join(input_folder, file), "r") as in_fh:
                    out_fh.write("\n".join([line.strip() for line in in_fh]))
                    out_fh.write("\n")

