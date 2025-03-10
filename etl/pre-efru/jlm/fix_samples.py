import csv
import argparse
import sys
from pprint import pprint

def main(source_file):
    reader = csv.reader(open(source_file))
    writer=csv.DictWriter(sys.stdout,
                          ['Sample',
                           'Location',
                           'Material',
                           'Result',
                           'Regulated Level',
                           'Concentration',
                           'Friable',
                           'Condition'
                           ],
                          dialect='unix')
    headers=[]
    rowlen = 0
    for row in reader:
        destrow={}
        if len(row) > 2 and row[0].startswith('Sample'):
            if len(headers) == 0:
                rowlen = len(row)
                for col in row:
                    headers.append(col.strip())
                writer.writeheader()
        elif len(row) == rowlen and row[1].strip() != '':
            for i in range(rowlen):
                if headers[i] == 'Sample #':
                    destrow['Sample'] = row[i]
                else:
                    destrow[headers[i]] = row[i]
            writer.writerow(destrow)

                    
            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source_file", help="raw csv location file")
    args = parser.parse_args()
    main(args.source_file)
