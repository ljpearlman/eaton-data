import argparse
from efru_util import SampleFile, Sample, Result, row_to_tokens, after_colon, debug_cols, is_empty, ColumnNumbers
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
    format = None
    
    while True:
        try:
            row = reader.__next__()
        except StopIteration:
            for sample in dust_samples.values():
                sample.write()
            return
            
        if re.match('HEAVY.*METALS.*IN.*SOIL.*', row[0]):
            format = 'Soil'
            collection_method = 'Soil'
            cn = ColumnNumbers()
            continue
        elif re.match('HEAVY.*METALS.*IN.*DUST.*', row[0]):
            format = 'Dust-1'
            collection_method = 'Dust'
            cn = ColumnNumbers()
            prev_cn = cn
            in_dust_header = True
            continue
        elif re.match('(?s).*Lead Dust Wipe Results.*', row[0]):
            format = 'Dust-2'
            substance = 'Lead'
            collection_method = 'Dust'
            cn = ColumnNumbers()
            continue

        if format == 'Soil':
            sample_id_col = SampleFile.find_column('Sample .*', row)
            if sample_id_col >= 0:
                sample_id = normalize_sample_id(row[sample_id_col].split()[1], collection_method)
                sample_attrs = {
                    'location': row[sample_id_col].split(' ', 2)[2],
                    'collection_method': collection_method,
                    'collection_date': collection_date
                }
                sample = Sample(sample_file, sample_id, sample_attrs)
                sample.write()

            elif cn.get('measurement') < 0:
                cn.set_column_numbers({
                    'substance': ['Heavy Metals Element.*'],
                    'reporting_limit': ['Detection Limit.*'],
                    'measurement': ['Results.*']
                }, row)
                cn.set('sample_id', sample_id_col)
                units = re.sub('Results *\((.*)\)', r'\1', row[cn.get('measurement')])

            elif is_empty(row[cn.get('substance')]) \
                 or row[cn.get('substance')].startswith('*NOTE') \
                 or row[cn.get('substance')].startswith('Heavy Metals Element'):
                pass
            else:
                result_attrs = {
                    'substance': fix_substance(row[cn.get('substance')]),
                    'reporting_limit': row[cn.get('reporting_limit')],
                    'units': units,
                    'measurement': row[cn.get('measurement')]
                }
                result = Result(sample, result_attrs)
                result.write()
                
        elif format == 'Dust-1':
            # Format is:
            #    <substance>
            # then
            #    ,.., "Sample # - Location",.., "Results (<units>)",..,"Reporting limit (<units>),..
            # or
            #    ,.., "Sample # - Location  I Results (<units>) I Reporting limit (<units>),..
            # then multiple
            #   Sample #<number> - <location>,..,<result>,..,<reporting_limit>,..
            # then
            # *Note.*
            
            if in_dust_header:
                substance_col = SampleFile.find_column('.+', row)
                if row[substance_col] and not row[substance_col].startswith('Sample') \
                   and not is_empty(row[substance_col]):
                    result_attrs = {'substance': fix_substance(row[substance_col])}
                    cn.set('substance', substance_col)

                units = None
                if cn.get('sample_id') < 0 or row[cn.get('sample_id')].startswith('Sample # - Location'):
                    cn.set_column_numbers ({
                        'sample_id': ['Sample.*'],
                        'measurement': ['Results.*'],
                        'reporting_limit': ['Reporting Limit.*']
                    }, row)
                    
                    if cn.get('sample_id') >= 0:
                        if cn.get('measurement') < 0:
                            # terrible hack - assume the previous column numbers are still good
                            cn = prev_cn
                        in_dust_header = False
                        if row[cn.get('measurement')].startswith('Results'):
                            units = fix_units(row[cn.get('measurement')])
                        elif re.match('.*Results.*', row[cn.get('sample_id')]):
                            units = fix_units(row[cn.get('sample_id')])
                        
            else:
                if row[cn.get('sample_id')] and row[cn.get('reporting_limit')]:
                    # Terrible hack - sometimes measurement is one column late
                    meas_col = cn.get('measurement')
                    if not row[meas_col]:
                        meas_col = meas_col + 1
                    if row[meas_col]:
                        (sample_id, location) = row[cn.get('sample_id')].split('-', 1)
                        sample_id = normalize_sample_id(sample_id, collection_method)
                        sample = dust_samples.get(sample_id)
                        if sample is None:
                            sample = Sample(sample_file, sample_id, {
                                'location': location,
                                'collection_method': collection_method,
                                'collection_date': collection_date
                            })
                            dust_samples[sample_id] = sample

                        result_attrs['measurement'] = row[meas_col]
                        result_attrs['reporting_limit'] = row[cn.get('reporting_limit')]
                        result_attrs['units'] = units
                        result = Result(sample, result_attrs)
                        result.write()
                elif cn.get('sample_id') >= 0 and row[cn.get('sample_id')].startswith('*NOTE'):
                    prev_cn = cn
                    cn = ColumnNumbers()
                    in_dust_header = True
                    result_attrs = {}
                    
        elif format == 'Dust-2':
            if cn.get('sample_id') < 0:
                cn.set_column_numbers({
                    'sample_id': ['Sample#'],
                    'location': ['Location'],
                    'measurement': ['Lead Concentration']
                }, row)
            elif row[0].startswith('The'):
                format = None
            else:
                sample = Sample(sample_file,
                                row[cn.get('sample_id')],
                                {
                                    'location': row[cn.get('location')],
                                    'collection_method': collection_method,
                                    'collection_date': collection_date
                                })
                sample.write()
                m = re.match('(<?[0-9.]+) *(.*)', row[cn.get('measurement')])
                result = Result(sample, {
                    'substance': 'Lead',
                    'measurement': m.groups()[0],
                    'units': m.groups()[1]
                })
                result.write()
                

def normalize_sample_id(sample_id, collection_method):
    sample_id = re.sub('Sam.le ?#','',sample_id)
    if sample_id == 'DI-':
        sample_id = '01'
    return collection_method + '-' + sample_id.strip()

def fix_units(results_string):
    return re.sub('.*Results *\((.*)\).*', r'\1', results_string)

def fix_substance(substance):
    return 'Copper' if substance == 'Coooer' else substance

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument("--original-filename")
    parser.add_argument("--date")
    args = parser.parse_args()
    main(args.file, args.original_filename, args.date)
