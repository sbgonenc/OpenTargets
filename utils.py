import pandas as pd
import ast


def convert_json2pandas(jsonfile: str, output_file: str = None) -> pd.DataFrame:
    """
    :param jsonfile: The path for the Json file in Json lines format
        Line1-  {"key" : "value"}
        Line2-  {"key" : "value"}
    :param  output_file: saves the pandas dataframe as table to this path. Does not save if None
    :return: pandas dataframe
    """
    from pandas import json_normalize
    import json

    with open(jsonfile, "r") as fh:
        pd_df = json_normalize([json.loads(json_line) for json_line in fh])

        if output_file is not None and isinstance(output_file, str):
            pd_df.to_csv(output_file, sep="\t", index=False)

    return pd_df


def convert_to_list(string):
    try:
        return ast.literal_eval(string)
    except (ValueError, SyntaxError) as e:
        print(f"Error at\n {string}")
        raise e


## Get location values
def get_loc_values(x:dict):
    return x.get("location", None), x.get("labelSL", None)

# convert_json2pandas("/home/berk/Projects/OpenTargets/data/combined_moa.json", "moa.tsv")
# convert_json2pandas("/home/berk/Projects/OpenTargets/data/combined_molecule.json", "molecules.tsv")
# convert_json2pandas("/home/berk/Projects/OpenTargets/data/combined_targets.json", "targets.tsv")
