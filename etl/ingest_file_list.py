import sys
from pathlib import Path
import re

def main(dirpath):
    dir = Path(dirpath)
    ex = re.compile('(ID[0-9]*)[A-Z]*')
    for file in dir.iterdir():
        m = ex.match(file.stem)
        if m:
            print(f"{file.name},{m.group(1)}")

if __name__ == '__main__':
    main('data/Test_Results_REDACTED')
