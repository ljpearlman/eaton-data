import argparse
from efru_util import SampleFile, Sample, Result
import csv
import json
import sys
import re

def main(file, original_filename):
    reader = csv.reader(open(file))
    sample_file = SampleFile(file, original_filename = original_filename)
    sample_file.write_sample_header()
    sample_file.write_result_header()
    
    section = 'sample_header'
    sample_attrs = {}
    result_attrs = {}

    for row in reader:
        if row[0].startswith('Sample ID'):
            fill_attrs(row, sample_attrs, {"Lab ID": "lab_id", "Collected" : 'collection_date'})
            section = 'sample_header'
        elif section == 'sample_header':
            if row[0].startswith("Method:"):
                sample_attrs["analysis_method"] = row[0].removeprefix("Method: ")
            elif row[0].startswith("Prep Method:"):
                sample_attrs["prep_method"] = row[0].removeprefix("Prep Method: ")
                section = 'results'
                result_attrs = {}                
                sample = Sample(sample_file, sample_id, sample_attrs)
                sample.write()
            elif re.match(".*Analyte Result.*", row[0]):
                pass
            else:
                sample_info = row[0].split(' ', 1)
                sample_id = sample_info[0]
                sample_attrs["location"] = sample_info[1]
        else:
            # Three alternatives:
            # Version 1
            #   Column 0: substance + measurement
            #   Column 1: empty
            #   Column 2: units
            #   Column 3: RL + DF
            #
            # Version 2
            #   Column 0: substance + measurement + units
            #   Column 1: empty
            #   Column 2: RL + DF
            #
            # Version 3:
            #   Column 0: substance + measurement
            #   Column 1: units
            #   Column 2: RL
            
            subrow = row[0].split(' ', 2)
            result_attrs = {'substance' : subrow[0]}
            if len(subrow) == 2:
                result_attrs['measurement'] = subrow[1]
                if row[1] == '':
                    result_attrs['units'] = row[2]
                    result_attrs['reporting_limit'] = row[3].split()[0]
                else:
                    result_attrs['units'] = row[1]
                    result_attrs['reporting_limit'] = row[2]
            else:
                result_attrs['measurement'] = subrow[1]                
                result_attrs['units'] = subrow[2]
                result_attrs['reporting_limit'] = row[2].split()[0]

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
