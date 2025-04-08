import argparse
from efru_util import SampleFile, Sample, Result, row_to_tokens, after_colon, debug_cols, is_empty, ColumnNumbers, nonempty
import csv
import json
import sys
import re

def main(file, original_filename, collection_date):
    reader = csv.reader(open(file))
    sample_file = SampleFile(file, original_filename = original_filename)
    sample_file.write_sample_header()
    sample_file.write_result_header()
    
    collection_method = None
    sample_attrs = {}
    result_attrs = {}
    substance = None
    report_type = None
    in_header = False
    cn = None
    units = None
    
    while True:
        try:
            row = reader.__next__()
        except StopIteration:
            return

        if re.match('(?s).*by Polarized Light Microscopy.*', row[0]):
            lab_methods = 'PLM'            
        if re.match('(?s).*Estimation by %.*', row[0]):
            units = '%'            
        if re.match('(?s).*Combustion Product Summary', row[0]):
            report_type = 'combustion_summary'
            in_header = True
            continue
        if re.match('(?s).*Wildfire Residue Analysis.*PLM.*Detail*', row[0]):
            report_type = 'wildfire_residue'
            in_header = True
            new_sample = True
            continue

        if report_type == 'combustion_summary':
            if in_header:
                cn = ColumnNumbers()
                cn.set_column_numbers(
                    {
                        'sample_id': ['Sample #'],
                        'lab_id' : ['Lab #'],
                        'location': ['Description'],
                        'char': ['Char'],
                        'ash': ['Ash'],
                        'soot': ['Soot']
                    },
                    row,
                    extra_keys = ['char', 'ash', 'soot']
                )
                if cn.number('sample_id') >= 0:
                    in_header = False
            elif cn.value('sample_id', row).startswith('Level Concentrations'):
                in_header = True
            elif cn.value('sample_id', row) and cn.value('sample_id', row) != 'Sample #':
                sample_attrs = {
                    'lab_id': cn.value('lab_id', row),
                    'location': cn.value('location', row),
                    'collection_method': collection_method_from_sample_id(
                        cn.value('sample_id', row)),
                    'lab_methods': lab_methods,
                    'collection_date': collection_date
                }
                sample = Sample(sample_file, cn.value('sample_id', row), sample_attrs)
                sample.write()
                for substance in ['char', 'ash', 'soot']:
                    result_attrs = {
                        'substance': substance,
                        'measurement': cn.value(substance, row),
                        'units': units
                    }
                    result = Result(sample, result_attrs)
                    result.write()
            
        if report_type == 'wildfire_residue':
            if in_header:
                cn = ColumnNumbers()                
                cn.set_column_numbers({
                    'sample_id': ['Sample #'],
                    'lab_id': ['Lab #'],
                    'location': ['Description'],
                    'measurement': ['Loading'],
                    'substance': ['Sample #']

                }, row)
            if cn.value('sample_id', row).startswith('Sample #') or row[0].startswith('Sample #'):
                in_header = False
                new_sample = True
            elif new_sample:
                sample_id = cn.value('sample_id', row)
                if sample_id:
                    # Sometimes sample id, lab id, and location wind up in one cell
                    if is_empty(cn.value('lab_id', row)) and is_empty(cn.value('location', row)):
                        (sample_id, lab_id, location) = re.split('\s+', cn.value('sample_id', row), 2)
                    else:
                        lab_id = cn.value('lab_id', row)
                        location = cn.value('location', row)
                    sample_attrs = {
                        'lab_id': lab_id,
                        'location': location,
                        'collection_method': collection_method_from_sample_id(sample_id),
                        'lab_methods': lab_methods,
                        'collection_date': collection_date
                    }
                    sample = Sample(sample_file, sample_id, sample_attrs)
                    sample.write()
                    in_header = False
                    new_sample = False
            elif cn.value('substance', row) == 'Total wildfire residue' or \
                 'Total wildfire residue' in row:
                in_header = True
                new_sample = False
#            elif cn.value('sample_id', row) and not cn.value('lab_id', row) and not cn.value('measurement', row):
#                report_type = None
            elif cn.value('substance', row) and not re.match('(?s)^Char|.*Ash\n?|.*Soot$', cn.value('substance', row)):
                result_attrs = {
                    'substance': cn.value('substance', row),
                    'measurement': cn.value('measurement', row),
                    'units': units
                }
                result = Result(sample, result_attrs)
                result.write()
                
def collection_method_from_sample_id(id):
    if id.startswith('T'):
        return('Tape')
    if id.startswith('W'):
        return('Wipe')
    return None
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--original-filename")
    parser.add_argument("--date")
    args = parser.parse_args()
    main(args.file, args.original_filename, args.date)
