import os

from settings import OPENTARGETS_LINK, DATA_VERSION, DATA_TYPE
from utils import call_subprocess

def download_OT_dataset(data_name, out_dir):
    """
    Downloads the OpenTargets dataset from the link specified in settings.py
    """

    os.chdir(out_dir)

    download_url = f"{OPENTARGETS_LINK}/{DATA_VERSION}/output/etl/{DATA_TYPE}/{data_name}"

    download_params = ["--recursive", "--no-parent", "--no-host-directories", "--cut-dirs", "8", download_url]

    return_code, _ = call_subprocess("wget", download_params)

    if return_code != 0:
        raise Exception("Download failed")

    return f"{DATA_TYPE}_{DATA_VERSION}.json"