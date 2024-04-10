## This script calls parsing methods, combines data, analyses

## output --> drug modelities (drugType from molecule) distribution on subcellular locations (subcellularLocations key from Targets)

## 1. Inspect and describe the starting datasets.
## 2. Prepare the relevant data by integrating the provided datasets to effectively link drug
## modalities to the subcellular locations of their targets.
## 3. Explore and identify any significant differences in the distribution of drug modalities
## across various subcellular locations.
## 4. Enhance the analysis with visualisations that illustrate your results.

def download_files():
    from lib.download_data import DownloadPrepareInitialData
    init_data_obj = DownloadPrepareInitialData()
    init_data_obj.process()
    return init_data_obj.get_combined_files()

def run_data_analysis(args):
    """
    Downloads, combines files and runs the data analysis
    :param args:
    :return:
    """
    ## Get data files
    download = args.do_not_download and args.combined_file is None
    targets_file, moa_file, drugs_file = download_files() if download else (None, None, None)

    from lib.data_process import DataProcess
    dataprocess_obj = DataProcess(
        targets_file=targets_file,
        mechanism_of_action_file=moa_file,
        molecules_file=drugs_file,
        combined_file=args.combined_file,
        drug_modality=args.drug_modality,
        location_key=args.location_key,
        save_preprocess_data=args.save_process_data,
        out_dir=args.out_dir,
        temp_dir=args.temp_dir,
        show_only_significant=args.only_significant
    )
    ## Process the data
    dataprocess_obj.process()

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("--do_not_download", action="store_false", help="Does not downloads the data if --combined_file is given.", required=False)
    parser.add_argument("--combined_file", type=str, help="Combined file for all data", required=False, default=None)
    parser.add_argument("--drug_modality", type=str, help="Drug modality key", required=False, default="drugType")
    parser.add_argument("--location_key", type=str, help="Select from subcellular_location_label or subcellular_location", required=False, default="subcellular_location_label")
    parser.add_argument("--save_process_data", action="store_true", help="Save processed data", required=False, default=False)
    parser.add_argument("--out_dir", type=str, help="Output directory", required=False, default=None)
    parser.add_argument("--temp_dir", type=str, help="Temporary directory", required=False, default=None)
    parser.add_argument("--only_significant", action="store_true", help="Only report significant results", required=False, default=False)

    args = parser.parse_args()
    run_data_analysis(args)