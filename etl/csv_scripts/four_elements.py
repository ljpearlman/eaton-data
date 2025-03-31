import argparse
from efru_util import SampleFile, Sample, Result, row_to_tokens, after_colon, debug_cols, is_empty, ColumnNumbers
import csv
import json
import sys
import re


def main(file, original_filename, collection_date):
    reader = csv.reader(open(file))
    sample_file = SampleFile(file, original_filename = original_filename)
    sample_file.write_sample_header()
    sample_file.write_result_header()
    substance = None
    in_summary = False
    location = None
    
    while True:
        try:
            row = reader.__next__()
        except StopIteration:
            return

        if in_summary:
            if cn.number('location') > 0:
                location = re.sub('\n', ' ', cn.value('location', row))
                if location not in ['SAMPLE LOCATION']:
                    in_summary = False
            else:
                cn.set_column_numbers({
                    'location': ['SAMPLE LOCATION']
                }, row)

        if re.match('SUMMARY', row[0]):
            cn = ColumnNumbers()            
            in_summary = True
            location = None

        if re.match('(?s).*Analysis Report.*Total Lead \(Pb\).*', row[0]):
            substance = 'Lead'
            result_attrs = {'substance': 'Lead'}
            cn = ColumnNumbers()

        if substance == 'Lead':
            if cn.number('collection_method') < 0:
                processed_rows = 0
                cn.set_column_numbers({
                    'collection_method': ['(?s).*Matrix:.*'],
                    'lab_methods': ['(?s).*Method:.*'],
                    'samples_analyzed': ['(?s).*Samples Analyzed.*']
                }, row, extra_keys=['samples_analyzed'])
                sample_attrs = {
                    'collection_method': re.sub('(?s).*Matrix: ([^\n]*).*', r'\1',
                                                cn.value('collection_method', row)),
                    'lab_methods': re.sub('(?s).*Method: ([^\n]*).*', r'\1',
                                          cn.value('lab_methods', row)),
                    'collection_date': collection_date
                }
                if location:
                    sample_attrs['location'] = location

                samples_analyzed = re.sub('(?s).*Samples Analyzed: ([0-9]+).*', r'\1', cn.value('samples_analyzed', row))
                if samples_analyzed:
                    samples_analyzed = int(samples_analyzed)
                    
            elif cn.number('lab_id') < 0:
                cn.set_column_numbers({
                    'lab_id': ['Lab ID'],
                    'sample_id': ['Client Sample ID'],
                    'sample_area': ['Sample Area.*'],
                    'raw_rl': ['RL.*'],                    
                    'measurement': ['Results'],
                    'units': ['Units']
                }, row, extra_keys = ['sample_area', 'raw_rl'])
                sample_area_units = re.sub('Sample Area *\((.*)\).*', r'\1', cn.value('sample_area', row))
                rl_units = re.sub('RL in *(.*).*', r'\1', cn.value('raw_rl', row))
            elif processed_rows < samples_analyzed:
                sample_attrs = cn.sample_values(row, sample_attrs)
                sample = Sample(sample_file, cn.value('sample_id', row), sample_attrs)
                sample.write()

                result_attrs = cn.result_values(row)
                result_attrs['substance'] = substance
                sample_area = float(cn.value('sample_area', row))
                if sample_area_units in ['ft2'] and cn.value('units', row) in ['µg/ft²'] \
                   and rl_units in ['µg/wipe']:
                    result_attrs['reporting_limit'] = \
                       float(cn.value('raw_rl', row)) / sample_area
                result = Result(sample, result_attrs)
                result.write()
                processed_rows=processed_rows + 1
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--original-filename")
    parser.add_argument("--date")
    args = parser.parse_args()
    main(args.file, args.original_filename, args.date)
