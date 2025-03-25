import argparse
from efru_util import SampleFile, Sample, Result, row_to_tokens, after_colon
import csv
import json
import sys
import re



def main(file, original_filename):
    reader = csv.reader(open(file))
    sample_file = SampleFile(file, original_filename = original_filename)
    sample_file.write_sample_header()
    sample_file.write_result_header()
    
    in_headers=True
    sample_attrs = {}
    result_attrs = {}
    
    # First row is column headings
    row = reader.__next__()
    
    # Next row is just substance
    row = reader.__next__()
    substance = row[0]
    
    # Following rows are data

    while True:
        try:
            row = reader.__next__()
        except StopIteration:
            return

        sample_id = row[0].split()[0]
        sample_attrs = {
            'location': row[0].split(maxsplit=1)[1],
            'lab_id': row[1],
            'analysis_method': row[7],
            'collection_method': 'Wipe'
        }

        result_attrs = {
            'substance': substance,
            'measurement': row[2],
            'units': row[3],
            'reporting_limit': row[10]
        }

        sample = Sample(sample_file, sample_id, sample_attrs)
        sample.write()
        result = Result(sample, result_attrs)
        result.write()            

def fill_attrs(row, dest_attrs, attr_map):
    for i in range(len(row)):
        for k in attr_map.keys():
            if row[i].strip() in [k, k + ':']:
                dest_attrs[attr_map[k]] = row[i+1]
            elif row[i].strip().startswith(k):
                dest_attrs[attr_map[k]] = re.sub(f'^ *{k}:? *', '', row[i])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--original-filename")
    args = parser.parse_args()
    main(args.file, args.original_filename)
