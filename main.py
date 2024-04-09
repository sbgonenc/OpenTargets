## This script calls parsing methods, combines data, analyses

## output --> drug modelities (drugType from molecule) distribution on subcellular locations (subcellularLocations key from Targets)

## 1. Inspect and describe the starting datasets.
## 2. Prepare the relevant data by integrating the provided datasets to effectively link drug
## modalities to the subcellular locations of their targets.
## 3. Explore and identify any significant differences in the distribution of drug modalities
## across various subcellular locations.
## 4. Enhance the analysis with visualisations that illustrate your results.

def run_data_analysis(args):
    ## Download and combines data
    if not args.combined_file:
        from download_data import DownloadPrepareInitialData
        init_data_obj = DownloadPrepareInitialData(
            work_dir=args.data_dir
        )
        init_data_obj.process(download=args.download_data)

    from data_process import DataProcess
    dataprocess_obj = DataProcess(
        #targets_file=init_data_obj.targets_combined,
        #mechanism_of_action_file=init_data_obj.moa_combined,
        #molecules_file=init_data_obj.molecules_combined,
        combined_file=args.combined_file,
        drug_modality=args.drug_modality,
        location_key=args.location_key,
        save_preprocess_data=args.save_process_data,
        out_dir=args.out_dir,
        temp_dir=args.temp_dir
    )
    ## Process the data
    dataprocess_obj.process()

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("--download_data", action="store_true", help="Download the data", required=False)
    parser.add_argument("--data_dir", type=str, help="Looks here for downloaded folders. If no data, downloads them", required=False, default=None)
    parser.add_argument("--combined_file", type=str, help="Combined file for all data", required=False, default=None)
    parser.add_argument("--drug_modality", type=str, help="Drug modality key", required=False, default="drugType")
    parser.add_argument("--location_key", type=str, help="Select from subcellular_location_label or subcellular_location", required=False, default="subcellular_location_label")
    parser.add_argument("--save_process_data", action="store_true", help="Save processed data", required=False, default=False)
    parser.add_argument("--out_dir", type=str, help="Output directory")
    parser.add_argument("--temp_dir", type=str, help="Temporary directory", required=False, default=None)

    args = parser.parse_args()
    run_data_analysis(args)