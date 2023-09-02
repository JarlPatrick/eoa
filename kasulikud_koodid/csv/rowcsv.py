
"""
CSV parser (`parseCSV`) to find the contestants and info columns.
Each contestant is represented with a dictionary, with "special" fields
having separate keys and other ones being put under `fields`.

Note: some columns are **required** to be present. If there is no
available info about them, an empty column should be inserted as to make
sure that special columns don't accidentally get listed under other fields.
"""

import csv
import logging
import re

logging.basicConfig(level=logging.INFO)

# Columns that *must* be present in the file
# if any one of these is missing, an exception is raised
required = ('name', 'school', 'class', 'placement')

# Common names for "special" columns
specialMap = {
    'JRK': 'placement',
    'KOHT': 'placement',
    'ÕPILANE': 'name',
    'NIMI': 'name',
    'ÕPILASE NIMI': 'name',
    'KOOL': 'school',
    'KLASS': 'class',
    'KL': 'class',
    'JUHENDAJA': 'instructors',
    'JUHENDAJAD': 'instructors',
    'ÕPETAJA': 'instructors',
    'ÕPETAJAD': 'instructors',
}

def specialKey(s):
    u = re.sub("[.-/?]", "", s.upper())
    return specialMap.get(u, None)

def parseCsv(filename):
    contestants = []
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        # note: removing zero-width characters sometimes present in files
        rawColumns = list(re.sub('[\ufeff]', '', c).strip() for c in next(reader))

        # first simple check (the first column is *usually* the placement
        if rawColumns[0].isdigit():
            raise Exception('No header row')
        
        columns = [c for c in rawColumns if specialKey(c) is None]
        spColumns = [c for c in map(specialKey, rawColumns) if c is not None]

        logging.info(f'Columns: {columns}')
        logging.info(f'Special columns: {spColumns}')

        # second check: are all required columns present?
        for r in required:
            if r not in spColumns:
                raise Exception(f'Column "{r}" not found in data')
        
        for row in reader:
            contestant = {'fields': [], 'instructors': []}
            
            for c, f in zip(rawColumns, row):
                s = specialKey(c)
                if s is None:
                    contestant['fields'].append(f)
                elif s == 'instructors':
                    contestant['instructors'] = [i.strip() for i in re.split('[:/,]', f) if i.strip() not in ('', '-')]
                else:
                    contestant[s] = f
                    
            logging.info(contestant)
            # third check: does the number of other columns match?
            # this catches cases where an unescaped extra "," is in the file
            if len(contestant['fields']) != len(columns):
                raise Exception('Non-matching field length')
            
            contestants.append(contestant)
        
    return columns, contestants

        
