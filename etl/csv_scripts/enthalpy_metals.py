import argparse
from efru_util import SampleFile, Sample, Result, row_to_tokens, after_colon
import csv
import json
import sys
import re


# File structure:
#
# Actual column divisions vary, but each sample is represented as:
#
# (Headers):
# Sample ID: <sample_id> Lab ID: <lab_id> Collected <collected_date>
# Matrix: Wipe
# <lab_id> Analyte Result Qual Units RL DF Batch Prepared Analyzed Chemist
# Method : <analysis_method>
# Prep Method : <prep_method>
#
# (Result Rows):
# <substance> <result> <units> <rl> <df> ...


def main(file, original_filename):
    reader = csv.reader(open(file))
    sample_file = SampleFile(file, original_filename = original_filename)
    sample_file.write_sample_header()
    sample_file.write_result_header()
    
    in_heades=True
    sample_attrs = {}
    result_attrs = {}

    for row in reader:
        cols = row_to_tokens(row)
        sample_element_map = {
            'Lab ID': 'lab_id',
            'Collected': 'collection_date',
            'Matrix': 'sample_method',
            'Prep Method': 'prep_method'
        }
        if cols[0].startswith('Sample ID'):
            in_headers = True
            sample_id=after_colon(cols[0])
            sample_attrs = Sample.fill_elements(cols[1:], sample_element_map, {})
            sample_attrs['location'] = sample_id

        elif in_headers:
            if cols[0].startswith('Matrix'):
                sample_attrs = Sample.fill_elements(cols, sample_element_map, sample_attrs)
            elif cols[0].startswith('Method'):
                sample_attrs = Sample.fill_elements(cols, sample_element_map, sample_attrs)
            elif cols[0].startswith('Prep Method'):
                sample_attrs = Sample.fill_elements(cols, sample_element_map, sample_attrs)
                sample = Sample(sample_file, sample_id, sample_attrs)
                sample.write()
                in_headers = False                

        else:
            result_attrs = {
                'substance' : cols[0],
                'measurement' : cols[1],
                'units': cols[2],
                'reporting_limit': cols[3].split()[0]
            }
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
