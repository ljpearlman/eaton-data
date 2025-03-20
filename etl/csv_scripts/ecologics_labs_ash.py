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
    
    for row in reader:
        if row[0] == 'Sample #' or row[0] == '' or row[2] == 'Field Blank':
            continue
        sample_id = row[0]
        sample_attrs = {
            "lab_id" : row[1],
            "location" : row[2],
            "analysis_method" : "PLM-visual"
        }

        sample = Sample(sample_file, sample_id, sample_attrs)
        sample.write()
        result = Result(sample, {
            "substance": "Char",
            "measurement": row[3],
            "units": '%'
        })
        result.write()        
        result = Result(sample, {
            "substance": "Ash",
            "measurement": row[4],
            "units": '%'
        })
        result.write()
        result = Result(sample, {
            "substance": "Soot",
            "measurement": row[5],
            "units": '%'
        })
        result.write()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--original-filename")
    args = parser.parse_args()
    main(args.file, args.original_filename)
