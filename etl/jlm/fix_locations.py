import csv
import argparse
import sys

def main(source_file):
    reader = csv.reader(open(source_file))
    writer=csv.writer(sys.stdout, dialect='unix')
    for row in reader:
        for col in row:
            if col.startswith("Location: "):
                destrow=[row[1][len("Location: "):]]
            elif col.startswith("Comments: "):
                destrow.append([row[1][len("Comments: "):]])
                writer.writerow(destrow)
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source_file", help="raw csv location file")
    args = parser.parse_args()
    main(args.source_file)
