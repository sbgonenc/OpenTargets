import numpy as np
import pandas as pd
import ast
import os


def call_subprocess(command: str, params: list, outfile=None, chdir=None):
    import subprocess
    # When we want to pipe the result to a text file, then we have to use the outfile option.
    # If the program asks you to specify the output with -o etc. then leave the outfile param None
    if outfile:
        stdout_buffer = open(outfile, "wb", buffering=0)
    else:
        stdout_buffer = subprocess.PIPE

    popen_args = dict(
        args=[command] + params,
        preexec_fn=os.setsid,
        stdin=subprocess.DEVNULL,
        stdout=stdout_buffer,
        stderr=subprocess.PIPE,
        bufsize=0,
        cwd=chdir,
    )
    process = subprocess.Popen(**popen_args)
    stdout, stderr = process.communicate()

    return_code = process.returncode

    if return_code != 0:
        full_command = " ".join(popen_args['args'])
        raise Exception(full_command, stdout, stderr)
    retstdout = stdout.decode() if stdout is not None else None
    return return_code, retstdout


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
    """
    Convert literal string in dataframe to a format that can be evaluated
    :param string:
    :return:
    """
    if any([isinstance(string, list), isinstance(string, dict), string in [None, np.nan]]):
        return string
    try:
        return ast.literal_eval(string)
    except (ValueError, SyntaxError) as e:
        print(f"Error at\n {string}")
        raise e


# Function to calculate significance for a specific drug-location pair
def test_significance(data, column_name, row_name):
    """
    This function tests the significance of the association between a specific drug type and a subcellular location using Fisher's exact test.

    Args:
      data: cross tab with rows indexed
      column_name: column_name to analyze.
      row_name: row_name location to analyze.

    Returns:
      A tuple containing the p-value and odds ratio from the Fisher's exact test.
    """
    from scipy.stats import fisher_exact

    # Get contingency table for drug type vs location
    contingency_table = [[0, 0], [0, 0]]
    row_column = data[column_name][row_name]
    not_row_all_column = data[column_name].sum() - row_column
    all_row_not_column = data.loc[row_name].sum() - row_column
    not_row_not_column = data.sum().sum() - not_row_all_column - all_row_not_column + row_column
    contingency_table[0][0] = row_column ## column+row sum
    contingency_table[1][0] = all_row_not_column ## row - column
    contingency_table[0][1] = not_row_all_column
    contingency_table[1][1] = not_row_not_column

    # Perform Fisher's exact test
    odds_ratio, p_value = fisher_exact(contingency_table)

    return p_value, odds_ratio

def create_heatmap(contingency_table, x_name=None, y_name=None, log_transform=True):
    import seaborn as sns
    import numpy as np
    import matplotlib.pyplot as plt

    title = f"{x_name} distribution on {y_name}"

    if log_transform:
        contingency_table = np.log2(contingency_table + 1)
        title = f"{title} (Log Scale)"

    # Create a heatmap using seaborn
    sns.heatmap(contingency_table, annot=False, cmap="viridis")
    plt.title(title)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.show()