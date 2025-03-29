import argparse
from efru_util import SampleFile, Sample, Result, row_to_tokens, after_colon, debug_cols, is_empty
import csv
import json
import sys
import re

# Columns for soil section
# S_SAMP_COL = 1
# S_LOC_COL = S_SAMP_COL
# S_SUBST_COL = 1
# S_RL_COL = S_SUBST_COL + 15
# S_MEAS_COL = S_SUBST_COL + 28

# Columns for dust section
D_SAMP_COL = 7
D_LOC_COL = D_SAMP_COL
D_SUBST_COL = 7
D_MEAS_COL = D_SAMP_COL + 13
D_RL_COL = D_MEAS_COL + 6


def main(file, original_filename, collection_date):
    reader = csv.reader(open(file))
    sample_file = SampleFile(file, original_filename = original_filename)
    sample_file.write_sample_header()
    sample_file.write_result_header()
    
    collection_method = None
    sample_attrs = {}
    result_attrs = {}
    dust_samples = {}
    substance = None
    
    while True:
        try:
            row = reader.__next__()
        except StopIteration:
            for sample in dust_samples.values():
                sample.write()
            return
            
        if re.match('HEAVY.*METALS.*IN.*SOIL.*', row[0]):
            collection_method = 'Soil'
            cn = {}
            continue
        elif re.match('HEAVY.*METALS.*IN.*DUST.*', row[0]):
            collection_method = 'Dust'
            cn = {}            
            continue
        elif re.match('.*Lead Dust Wipe Results.*', row[0]):
            substance = 'Lead'
            collection_method = 'Dust'
            cn = {}            
            continue

        if collection_method == 'Soil':
            scol = SampleFile.find_column('Sample .*', row)
            if scol:
                sample_id = normalize_sample_id(scol.split()[1], collection_method)
                sample_attrs = {
                    'location': scol.split(' ', 2)[2],
                    'collection_method': collection_method,
                    'collection_date': collection_date
                }
                sample = Sample(sample_file, sample_id, sample_attrs)
                sample.write()

            elif not cn.get('measurement'):
                cn = SampleFile.find_column_numbers({
                    'substance': ['Heavy Metals Element.*'],
                    'reporting_limit': ['Detection Limit.*'],
                    'measurement': ['Results.*']
                }, row)
                if cn.get('substance') != cn['substance']:
                    print("substance col mismatch")
                if cn.get('reporting_limit') != cn['reporting_limit']:
                    print("reporting_limit col mismatch")
                if cn.get('measurement') != cn['measurement']:
                    print("measurement col mismatch")
                units = re.sub('Results *\((.*)\)', r'\1', row[cn['measurement']])

            elif is_empty(row[cn['substance']]) \
                 or row[cn['substance']].startswith('*NOTE') \
                 or row[cn['substance']].startswith('Heavy Metals Element'):
                pass
            else:
                result_attrs = {
                    'substance': 'Copper' if row[cn['substance']] == 'Coooer' else row[cn['substance']],
                    'reporting_limit': row[cn['reporting_limit']],
                    'units': units,
                    'measurement': row[cn['measurement']]
                }
                result = Result(sample, result_attrs)
                result.write()
        elif collection_method == 'Dust':
            # confusing because substance column in header is the same as
            # sample id column in body
            if not is_empty(row[D_SUBST_COL]) and is_empty(row[D_MEAS_COL]):
                result_attrs = {
                    'substance': 'Copper' if row[D_SUBST_COL] == 'Coooer' else row[D_SUBST_COL]
                }
                units = None
            elif row[D_SAMP_COL].startswith('*NOTE'):
                pass
            elif row[D_MEAS_COL].startswith('Results'):
                units = fix_units(row[D_MEAS_COL])
            elif row[D_SAMP_COL] and row[D_MEAS_COL] and row[D_RL_COL]:
                (sample_id, location) = row[D_SAMP_COL].split('-', 1)
                sample_id = normalize_sample_id(sample_id, collection_method)
                sample = dust_samples.get(sample_id)
                if sample is None:
                    sample = Sample(sample_file, sample_id, {
                        'location': location,
                        'collection_method': collection_method,
                        'collection_date': collection_date
                    })
                    dust_samples[sample_id] = sample
                result_attrs['measurement'] = row[D_MEAS_COL]
                result_attrs['reporting_limit'] = row[D_RL_COL]
                result_attrs['units'] = units
                result = Result(sample, result_attrs)
                result.write()

def normalize_sample_id(sample_id, collection_method):
    sample_id = re.sub('Sam.le ?#','',sample_id)
    if sample_id == 'DI-':
        sample_id = '01'
    return collection_method + '-' + sample_id.strip()

def fix_units(results_string):
    return re.sub('Results *\((.*)\)', r'\1', results_string)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--original-filename")
    parser.add_argument("--date")
    args = parser.parse_args()
    main(args.file, args.original_filename, args.date)
