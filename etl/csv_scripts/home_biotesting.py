import argparse
from efru_util import SampleFile, Sample, Result, row_to_tokens, after_colon, debug_cols
import csv
import json
import sys
import re

M_HEADER_COL = 11
M_SAMP_COL = 0
M_LAB_COL = M_SAMP_COL + 18
M_MEAS_COL = M_LAB_COL + 16
M_DF_COL = M_MEAS_COL + 4
M_METHOD_COL = M_DF_COL + 6
M_QUAL_DL_COL = M_METHOD_COL + 15
M_RL_COL = M_QUAL_DL_COL + 2

def main(file, original_filename, date, collection_method):
    reader = csv.reader(open(file))
    sample_file = SampleFile(file, original_filename = original_filename)
    sample_file.write_sample_header()
    sample_file.write_result_header()

    in_metals = False

    while True:
        try:
            row = reader.__next__()
        except StopIteration:
            return

        if len(row) > M_HEADER_COL and row[M_HEADER_COL].startswith('Metals Analysis'):
            in_metals = True
        elif in_metals:
            if row[0].startswith('Client Sample ID'):
                samp_col = 0
                i = 0
                for col in row:
                    if col.startswith('Lab ID'):
                        lab_col = i
                    elif col.startswith('Result'):
                        meas_col = i
                    elif col.startswith('Analyst'):
                        method_col = i
                    elif col.startswith('RL'):
                        rl_col = i
                    i = i + 1
            elif row[0].startswith('Analyst'):
                in_metals = False
            elif row[meas_col]:
                (substance, sample_id, location) = re.split('\s+', row[samp_col], maxsplit=2)
                lab_method = re.split('\s+', row[method_col], 1)[1]
                (measure, units) = re.split('\s+', row[meas_col], 1)                
                sample = Sample(sample_file, sample_id, {
                    'collection_date': date,
                    'location': location,
                    'lab_id': row[lab_col],
                    'lab_methods': lab_method
                })
                sample.write()
                result = Result(sample, {
                    'substance': substance,
                    'measurement': measure,
                    'units': units,
                    'reporting_limit': row[rl_col]
                })
                result.write()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--original-filename")
    parser.add_argument("date")
    parser.add_argument("collection_method")
    args = parser.parse_args()
    main(args.file, args.original_filename, args.date, args.collection_method)
