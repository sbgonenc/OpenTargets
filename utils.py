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

