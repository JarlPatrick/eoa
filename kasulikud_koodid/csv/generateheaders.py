
"""
Add a header row to a CSV file that doesn't already have them.
Based on common templates for these competitions.
These headers are required for the import script to function properly.
"""

import argparse


headerMap = {
    'efo': 'Koht,Nimi,Klass,Kool,Juhendaja,1,2,3,4,5,6,7,8,9,10,E1,E2,Kokku,Järk',
    'flv': 'Koht,Nimi,Klass,Kool,Juhendaja,1,2,3,4,5,6,7,8,9,10,Kokku,Järk'
}

parser = argparse.ArgumentParser(description='Add header row to a csv file')
parser.add_argument('type', help='The type of header to generate', choices=list(headerMap.keys()))
parser.add_argument('infile', type=argparse.FileType('r'), help='Input file')
parser.add_argument('outfile', type=argparse.FileType('w'), help='Output file')

args = parser.parse_args()

args.outfile.write(headerMap[args.type] + '\n')
args.outfile.write(args.infile.read())
