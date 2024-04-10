This project is to know how drug modalities distributed among subcellular locations using OpenTargets datasets (molecules, Targets, mechanism of action).

Set a virtual environment

```python3 -m venv  .venv```

Activate

```source .venv/bin/activate```

Install requirements

```pip install -r requirements.txt```

Run the script

```python3 main.py --out_dir /path/to/output/directory```

By default, the script downloads the data from OpenTargets API, combines data to "all_combined_data.tsv" and generates significance report in "drugType" and "subcellular_location_label".
However if you give "all_combined_data.tsv" as input to `--combined_file` flag, it continues analysis from that file.

```python3 main.py --out_dir /path/to/output/directory --combined_file /path/to/all_combined_data.tsv```

To determine the significance for the distribution of drug modalities among subcellular locations, it uses Fisher's exact test and reports in "significance_report.tsv".
The final `significance_report.tsv` , heatmap and barplot will be saved in the `--out_dir` output directory. 

Example Usage:

```python3 main.py  --combined_file ./all_combined_data.tsv --location_key subcellular_location_label --drug_modality actionType --only_significant```

You can also use `--only_significant` flag to get only significant results in the `significance_report.tsv` file.

For the `--drug_modality` flag you can select one of `actionType` , `drugType` , `targetType` , `biotype` 
and for the `--location_key` flag you can select either one of `subcellular_location_label` , `subcellular_location`
