import csv
import argparse
import sys

def main(source_file):
    reader = csv.reader(open(source_file))
    writer=csv.writer(sys.stdout, dialect='unix')
    destrow = []
    for row in reader:
        if row[0] == "Included in inspection?":
            destrow.append(row[1])
            writer.writerow(destrow)
            destrow=[]
        else:
            destrow.append(row[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source_file", help="raw csv location file")
    args = parser.parse_args()
    main(args.source_file)
    
