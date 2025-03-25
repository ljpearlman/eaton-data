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
    
    collection_method = None
    sample_attrs = {}
    result_attrs = {}
    
    while True:
        try:
            row = reader.__next__()
        except StopIteration:
            return

        if re.match('HEAVY.*METALS.*IN.*SOIL.*', row[0]):
            collection_method = 'Soil'
            continue
        elif re.match('HEAVY.*METALS.*IN.*DUST.*', row[0]):
            collection_method = 'Dust'
            continue

        if collection_method == 'Soil':
            if row[1].startswith('Sample'):
                sample_id = row[1].split()[1]
                if sample_id == 'DI-':
                    sample_id = '01'
                sample_id = 'Soil-' + sample_id
                sample_attrs = {
                    'location': row[1].split(' ', 2)[2],
                    'collection_method': collection_method
                }
                sample = Sample(sample_file, sample_id, sample_attrs)
                sample.write()
            elif row[1].startswith('Heavy') or row[1] is None or row[1].startswith('*NOTE'):
                pass
            else:
                result_attrs = {
                    'substance': 'Copper' if row[1] == 'Coooer' else row[1],
                    'reporting_limit': row[16],
                    'units': 'ug/ft2',
                    'measurement': row[29]
                }
                result = Result(sample, result_attrs)
                result.write()            
        elif collection_method == 'Dust':
            pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--original-filename")
    args = parser.parse_args()
    main(args.file, args.original_filename)
