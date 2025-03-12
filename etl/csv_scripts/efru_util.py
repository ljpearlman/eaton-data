import csv
from collections import OrderedDict
import sys
from pathlib import Path
import re

class SampleFile:
    base_headers = ["report_file", "sample_id"]
    sample_headers = [
        "lab_id",
        "collection_date",
        "location",
        "analysis_method",
        "prep_method"
    ]
    result_headers = [
        "substance",
        "measurement",
        "units",
        "reporting_limit"
    ]
    
    def __init__(self, report_file, result_dir="./processed", original_filename = None):
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
