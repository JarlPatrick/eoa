import csv
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=argparse.FileType("r"))
parser.add_argument("outfile", type=argparse.FileType("w"))
parser.add_argument("-m", "--mentor", action="store_true")
parser.add_argument("-g", "--grade")
parser.add_argument("-s", "--school", action="store_true")
parser.add_argument("-r", "--ranking")

args = parser.parse_args()

reader = csv.reader(args.infile, delimiter=',')
writer = csv.writer(args.outfile, delimiter=',')

header = next(reader)
rows = list(reader)

warn = logging.warning


def add_fill_col(name, fill, index = None):
    if header.count(name) > 0:
        warn(f"Column '{name}' already exists!")
        
    if index is None:
        index = len(header)
        
    header.insert(index, name)
    for r in rows:
        r.insert(index, fill)

def add_ranking(total_col):
    add_fill_col("Koht", "0", 0)

    ti = header.index(total_col)
    
    lastS = float("inf")
    currPlace = 0
    startPlace = 0
    starti = 0
    
    for i, row in enumerate(rows):
        s = float(row[ti].replace(",", "."))
        currPlace += 1
        if s < lastS:
            for ri in range(starti, i):
                rows[ri][0] = startPlace
            startPlace = currPlace
            starti = i
            lastS = s

    for ri in range(starti, len(rows)):
        rows[ri][0] = startPlace
        
if args.ranking:
    add_ranking(args.ranking)

if args.mentor:
    add_fill_col("Juhendaja", "")

if args.grade:
    if args.grade == "-":
        add_fill_col("Klass", "")
    else:
        add_fill_col("Klass", args.grade)

if args.school:
    add_fill_col("Kool", "")

writer.writerow(header)
for r in rows:
    writer.writerow(r)
