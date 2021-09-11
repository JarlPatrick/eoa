
"""
The graphical interface used to interface with `rowcsv` and `importoly`
in order to import subcontests from CSV files.

These modules might show debug information in the console and it is advised
to monitor such output to check against problems.

Note that `importoly` does not currently check for non-existant subjects /
types / years, creating new ones implicitly. Care should be taken to follow
the current conventions (capitalization, years being in the format "2000/2001").

The age group is currently handled differently, using the class range to
specify the age group. The min and max classes must *both* be present, even
if only a single class needs to be specified. These values can be separated by
a space or a comma. New age groups are *not* created automatically, as they
lack a name.

Example inputs:

Filename: mat_2000_9.csv
Contest name: Matemaatika lõppvoor 1999/2000
Subject: Matemaatika
Type: Lõppvoor
Year: 1999/2000
Subcontest name: 9. klassi õpilaste tulemused
Class range: 9,9
"""

from tkinter import *
import importoly
import rowcsv
import re

master = Tk()
master.geometry('400x600+400+300')


inputs = {
    'filename': 'Filename',
    'name': 'Contest name',
    'subject': 'Subject',
    'type': 'Type',
    'year': 'Year',
    'subName': 'Subcontest name',
    'classRange': 'Class range',
}


# Create inputs
for i, k in enumerate(inputs.keys()):
    label = Label(master, text=inputs[k])
    entry = Entry(master)
    label.grid(row = 2 * i, column = 0)
    entry.grid(row = 2 * i + 1, column = 0, sticky=N+S+E+W)
    inputs[k] = entry
    master.rowconfigure(2 * i, weight = 0)
    master.rowconfigure(2 * i + 1, weight = 1)

master.columnconfigure(0, weight=1)

"""
Handle a CSV file.

Note: wraps the subcontest in a contest, then calls `addContest`.
"""
def doSubmit():
    contest = {
        'name': inputs['name'].get(),
        'subject': inputs['subject'].get(),
        'type': inputs['type'].get(),
        'year': inputs['year'].get(),
    }
    subcontest = {
        'name': inputs['subName'].get(),
        'class_range': re.split('[\s,]', inputs['classRange'].get())
    }
    contest['subcontests'] = [subcontest]
    subcontest['columns'], subcontest['contestants'] = rowcsv.parseCsv(inputs['filename'].get())
    
    importoly.addContest(contest)
    
submit = Button(master, text='Submit', command=doSubmit)
submit.grid(row=2*len(inputs), column=0, sticky=N+S+E+W)
master.rowconfigure(2*len(inputs), weight=1)

mainloop()
