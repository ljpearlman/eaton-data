import csv
from collections import OrderedDict
import sys
from pathlib import Path
import re

def row_to_tokens(row, ignore_strings = ['', ':'], split_on_whitespace = False):
    result = []
    for col in row:
        if split_on_whitespace:
            vals = col.split()
        else:
            vals = [col.strip()]
        for val in vals:
            if val not in ignore_strings:
                result.append(val)
    return result

def after_colon(string):
    return string.split(':')[1].strip()

def debug_cols(row, all=False):
    i = 0
    for col in row:
        if all or col:
            print(f'{i}: {col}')
        i = i + 1

def is_empty(str):
    return str is None or str == ''

def fill_elements(cols, element_map, result_map):
    i = 0
    while i < len(cols):
        for k in element_map.keys():
            if cols[i] in (k, k + ':'):
                i = i + 1
                result_map[element_map[k]] = cols[i]
            elif cols[i].startswith(k):
                result_map[element_map[k]] = after_colon(cols[i])
        i = i+1
    return(result_map)


class SampleFile:
    base_headers = ["report_file", "sample_id"]
    sample_headers = [
        "lab_id",
        "collection_date",
        "location",
        "lab_methods",
        "collection_method"
    ]
    result_headers = [
        "substance",
        "measurement",
        "units",
        "reporting_limit"
    ]

  
    def __init__(self, report_file, result_dir=None, original_filename = None):
        if result_dir is None:
            result_dir = Path(report_file).parent / 'processed'
        result_dir.mkdir(exist_ok=True)
        if original_filename is None:
            original_filename = re.sub('(.*/)?(tabula-)?(.*).csv', r'\3.pdf', report_file)
        self.original_filename = original_filename

        sample_file = (Path(result_dir) / re.sub('.pdf', '_samples.csv', original_filename)).open("w")
        result_file = (Path(result_dir) / re.sub('.pdf', '_results.csv', original_filename)).open("w")
        self.sample_writer = csv.DictWriter(sample_file, self.base_headers + self.sample_headers)
        self.result_writer = csv.DictWriter(result_file, self.base_headers + self.result_headers)

    def write_sample_header(self):
        self.sample_writer.writeheader()

    def write_result_header(self):
        self.result_writer.writeheader()        

    def write_sample_row(self, row):
        row["report_file"] = self.original_filename
        self.sample_writer.writerow(row)

    def write_result_row(self, row):
        row["report_file"] = self.original_filename
        self.result_writer.writerow(row)

    @staticmethod
    def find_column(regexp, row):
        i = 0
        for col in row:
            if re.match(regexp, col):
                return i
            i = i + 1
        return -1

class ColumnNumbers:
    recognized_headers = SampleFile.base_headers + SampleFile.sample_headers + SampleFile.result_headers
    
    def __init__(self):
        self.cn = {}
        
    def set_column_numbers(self, label_map, row):
        # label_map is of the form:
        #    { column_name : [list_of regexes] }
        # row should be a header row
        # for each column in <row>, if that string matches one of the regexes in a list,
        #     that's assumed to be the column associated with that column name

        for key in label_map.keys():
            if key not in self.recognized_headers:
                raise ValueError(f'Unrecognized column "{key}"')

        i = 0
        for col in row:
            for key in label_map.keys():
                for regex in label_map[key]:
                    if re.match(regex, col):
                        self.cn[key] = i
            i = i + 1
            
    def get(self, label):
        return self.cn.get(label) if self.cn.get(label) is not None else -1

    def set(self, label, val):
        self.cn[label] = val
        

class Sample(OrderedDict):
    def __init__(self, sample_file, sample_id, sample_attrs):
        self.sample_file = sample_file
        self["sample_id"] = sample_id
        for key in sample_attrs.keys():
            if key not in SampleFile.sample_headers:
                raise RuntimeError(f"keyword arg {key} not recognized")
        for h in SampleFile.sample_headers:
            self[h] = sample_attrs.get(h)

    def write(self):
        self.sample_file.write_sample_row(self)

    def write_result_row(self, row):
        row["sample_id"] = self["sample_id"]
        self.sample_file.write_result_row(row)

    @classmethod
    def fill_elements(cls, cols, element_map, result_map):
        for k in element_map.values():
            if k not in SampleFile.sample_headers:
                raise ValueError(f'{k} is not a recognized Sample header')
        return fill_elements(cols, element_map, result_map)


class Result(OrderedDict):
    def __init__(self, sample, result_attrs):
        self.sample = sample
        for key in result_attrs.keys():
            if key not in SampleFile.result_headers:
                raise RuntimeError(f"keyword arg {key} not recognized")
        for h in SampleFile.result_headers:
            self[h] = result_attrs.get(h)

    def write(self):
        self.sample.write_result_row(self)

    def fill_elements(cls, cols, element_map, result_map):
        for k in element_map.values():
            if k not in SampleFile.result_headers:
                raise ValueError(f'{k} is not a recognized Result header')

        return fill_elements(cols, element_map, result_map)

