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

            elif cn.number('measurement') < 0:
                cn.set_column_numbers({
                    'substance': ['Heavy Metals Element.*'],
                    'reporting_limit': ['Detection Limit.*'],
                    'measurement': ['Results.*']
                }, row)
                units = re.sub('Results *\((.*)\)', r'\1', cn.value('measurement', row))

            elif is_empty(cn.value('substance', row)) \
                 or cn.value('substance', row).startswith('*NOTE') \
                 or cn.value('substance', row).startswith('Heavy Metals Element'):
                pass
            else:
                result_attrs = {
                    'substance': fix_substance(cn.value('substance', row)),
                    'reporting_limit': cn.value('reporting_limit', row),
                    'units': units,
                    'measurement': cn.value('measurement', row)
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
                   and nonempty(row[substance_col]):
                    result_attrs = {'substance': fix_substance(row[substance_col])}
                    cn.set('substance', substance_col)

                units = None
                if cn.number('sample_id') < 0 or cn.value('sample_id', row).startswith('Sample # - Location'):
                    cn.set_column_numbers ({
                        'sample_id': ['Sample.*'],
                        'measurement': ['Results.*'],
                        'reporting_limit': ['Reporting Limit.*']
                    }, row)
                    
                    if cn.number('sample_id') >= 0:
                        if cn.number('measurement') < 0:
                            # terrible hack - assume the previous column numbers are still good
                            cn = prev_cn
                        in_dust_header = False
                        if cn.value('measurement', row).startswith('Results'):
                            units = fix_units(cn.value('measurement', row))
                        elif re.match('.*Results.*', cn.value('sample_id', row)):
                            units = fix_units(cn.value('sample_id', row))
                        
            else:
                if nonempty(cn.value('sample_id', row)) and nonempty(cn.value('reporting_limit', row)):
                    # Terrible hack - sometimes measurement is one column late
                    meas_col = cn.number('measurement')
                    if is_empty(row[meas_col]):
                        meas_col = meas_col + 1
                    if nonempty(row[meas_col]):
                        (sample_id, location) = cn.value('sample_id', row).split('-', 1)
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
                        result_attrs['reporting_limit'] = cn.value('reporting_limit', row)
                        result_attrs['units'] = units
                        result = Result(sample, result_attrs)
                        result.write()
                elif cn.value('sample_id', row).startswith('*NOTE'):
                    prev_cn = cn
                    cn = ColumnNumbers()
                    in_dust_header = True
                    result_attrs = {}
                    
        elif format == 'Dust-2':
            if cn.number('sample_id') < 0:
                cn.set_column_numbers({
                    'sample_id': ['Sample#'],
                    'location': ['Location'],
                    'measurement': ['Lead Concentration']
                }, row)
            elif row[0].startswith('The'):
                format = None
            else:
                sample = Sample(sample_file,
                                cn.value('sample_id', row),
                                {
                                    'location': cn.value('location', row),
                                    'collection_method': collection_method,
                                    'collection_date': collection_date
                                })
                sample.write()
                m = re.match('(<?[0-9.]+) *(.*)', cn.value('measurement', row))
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
