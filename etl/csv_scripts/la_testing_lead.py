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
    
    row = reader.__next__()
        
    while row:
        try:
            row = row_to_tokens(reader.__next__(), split_on_whitespace=True)
        except StopIteration:
            return
            
        sample_attrs = {
            'prep_method': 'EPA 3050B',
            'analysis_method': 'EPA 7000B'
        }
        result_attrs = {
            'substance': 'Lead'
        }
        sample_id = row[0]
        sample_attrs['collection_date'] = row[1]
        result_attrs['reporting_limit'] = row[5]
        result_attrs['measurement'] = row[7]
        result_attrs['units'] = "ug/ft2" if row[8] == "\u03bcg/ft2" else row[8]
        
        row = reader.__next__()
        sample_attrs['lab_id'] = row[0]
        sample_attrs['location'] = row[1].split(':')[1].strip()

        row = reader.__next__()
        sample_attrs['collection_method'] = row[1].split()[1].strip()

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
