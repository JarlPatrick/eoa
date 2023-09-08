import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox as tkmsg
import re
import csv
import logging
import importoly

contestFields = [
    {"name": "name", "display": "Contest name"},
    {"name": "subject", "display": "Subject"},
    {"name": "type", "display": "Type"},
    {"name": "year", "display": "Year"},
    {"name": "subcontest_name", "display": "Subcontest name"},
    {"name": "class_range", "display": "Class range"},
]

subcontestNames = {"subcontest_name", "class_range"}

specialColumns = [
    {"name": "placement", "color": "#dd3030"},
    {"name": "name", "color": "#30dd30"},
    {"name": "class", "color": "#7070dd"},
    {"name": "school", "color": "#3030dd"},
    {"name": "instructors", "color": "#f78a2f"}
]

inferContest = {
    "subject": [
        {"pattern": "efo|fyysika|füüsika|fys", "value": "Füüsika"},
        {"pattern": "emo|mat|lvs|lvt", "value": "Matemaatika"},
        {"pattern": "eko|keemia", "value": "Keemia"},
        {"pattern": "inf", "value": "Informaatika"},
    ],
    "type": [
        {"pattern": "lv[0-9st]", "value": "Lahtine"},
        {"pattern": "lv", "value": "Lõppvoor"},
        {"pattern": "lah", "value": "Lahtine"},
    ],
    "class_range": [
        {"pattern": "[^1-9]8kl", "value": "8,8,8"},
        {"pattern": "[^1-9]9kl", "value": "9,9,9"},
        {"pattern": "10kl", "value": "10,10,10"},
        {"pattern": "11kl", "value": "11,11,11"},
        {"pattern": "12kl", "value": "12,12,12"},
        {"pattern": "[-_]g($|[-_.])", "value": "gümnaasium,10,12"},
        {"pattern": "[-_]pk?($|[-_.])", "value": "põhikool,8,9"},
        {"pattern": "[-_]v($|[-_.])", "value": "vanem,11,12"},
        {"pattern": "[-_]n($|[-_.])", "value": "noorem,9,10"},
    ]
}

inferColumns = [
    {"pattern": r"(jrk|koht)\.?", "value": "placement"},
    {"pattern": r"(õpilane|(õpilase )?nimi)\.?", "value": "name"},
    {"pattern": r"kool\.?", "value": "school"},
    {"pattern": r"kl(ass)?\.?", "value": "class"},
    {"pattern": r".*(juhendajad?|õp(etaja)?).*", "value": "instructors"},
]



def warn(text):
    logging.warning(text)
    tkmsg.showwarning(message=text)


class ScrollableFrame(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        self.root = root
        self.canvas = tk.Canvas(self.root)
        super().__init__(self.canvas, *args, **kwargs)
        self.canvas.create_window(0, 0, window=self, anchor=tk.NW)
        
        def onScroll(event):
            self.canvas.yview_scroll(-1 if event.num == 4 else 1, "units")

        self.canvas.bind_all("<Button-4>", onScroll)
        self.canvas.bind_all("<Button-5>", onScroll)
        
        self.bind("<Configure>", lambda *_: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def pack(self, *args, **kwargs):
        self.canvas.pack(*args, **kwargs)
        
    def setYScrollbar(self, scrollbar):
        scrollbar.configure(command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

def setEntry(entry, value):
    entry.delete(0, tk.END)
    entry.insert(0, value)

selectedField = None

def selectField(ri, ci):
    global selectedField
    if selectedField is not None:
        currentGrid[selectedField[0]][selectedField[1]].configure(font="sans 11")
    currentGrid[ri][ci].configure(font="sans 11 bold")
    selectedField = (ri, ci)
    setEntry(editField, currentGrid[ri][ci]["text"])

def fieldButton(ri, ci):
    def action(*_):
        selectField(ri, ci)
    return action

def clearGrid():
    global selectedField

    for row in currentGrid:
        for field in row:
            field.destroy()
    currentGrid.clear()
    selectedField = None
    for sc in specialColumns:
        sc["coli"] = None 

"""
Set the grid to a 2D list of values
"""
def setGrid(grid):
    clearGrid()
    for ri, row in enumerate(grid):
        newRow = []
        currentGrid.append(newRow)
        for ci, field in enumerate(row):
            e = tk.Button(gridWrapper, text=field, command=fieldButton(ri, ci))
            e.grid(row=ri, column=ci, sticky="nsew")
            newRow.append(e)
    

"""
Parse a CSV file into the editor
"""
def parseCSV(inFile):
    # read all of the data into a list
    reader = csv.reader(inFile, delimiter=",")
    newGrid = []
    maxLength = -1 # keep track of the max and min row lengths
    warnLengthMismatch = False
    for row in reader:
        # note: removing zero-width characters sometimes present in files
        fields = list(re.sub("[\ufeff]", "", f).strip() for f in row)
        newGrid.append(fields)
        length = len(fields)
        if length != maxLength:
            if maxLength != -1:
                warnLengthMismatch = True
            maxLength = max(maxLength, length)

    clearGrid()

    if warnLengthMismatch:
        warn("Row lengths are non-uniform!")
        # attempt to fix the problem
        for row in newGrid:
            row += ["" for _ in range(maxLength - len(row))]

    # import the data into the editor
    setGrid(newGrid)
def findName(seq, name):
    for field in seq:
        if field["name"] == name:
            return field

"""
Infer the content of some fields based on the filename and column names
"""
def inferFields(filename):
    # Contest info
        
    for fieldName, patterns in inferContest.items():
        field = findName(contestFields, fieldName)
        if not field["lock"].get():
            for pattern in patterns:
                if re.search(pattern["pattern"], filename, re.IGNORECASE):
                    setEntry(field["entry"], pattern["value"])
                    break

    # Special case for the year   
    year = findName(contestFields, "year")
    if not year["lock"].get():
        m = re.search(r"(?:^|\D)(\d{4})\D(\d{2}(:?\d{2})?)(?:$|\D)", filename)
        if m:
            y1 = m.group(1)
            y2 = m.group(2)
            if str(int(y1) + 1).endswith(y2):
                y2 = str(int(y1) + 1)
                setEntry(year["entry"], f"{y1}")

    # Columns
    for ci, name in enumerate(currentGrid[0]):
        for pattern in inferColumns:
            if re.match(pattern["pattern"], name["text"], re.IGNORECASE):
                findName(specialColumns, pattern["value"])["coli"] = ci
                break
    highlightGrid()

"""
"Open file" action performed
"""
def openFile():
    # file dialog
    filename = askopenfilename(filetypes=[("CSV",".csv"), ("File", "*")])
    if filename == ():
        # cancelled
        return
    
    print(filename)
    with open(filename) as inFile:
        parseCSV(inFile)

    inferFields(filename)
    highlightGrid()

def highlightGrid():
    # clear any highlighting
    for row in currentGrid:
        for field in row:
            field.configure(background=defaultColor)
    
    for sc in specialColumns:
        if sc["coli"] is not None:
            for row in currentGrid:
                row[sc["coli"]].configure(background=sc["color"])

def importTable(*_):
    if any(field["entry"].get() == "" for field in contestFields):
        warn("Missing contest information")
        return

    sc = set(col["coli"] for col in specialColumns if col["coli"] is not None)
    if len(sc) != len(specialColumns):
        warn("Missing required columns")
        return
    
    sc = {col["coli"]: col["name"] for col in specialColumns}
    
    contest = {
        field["name"]: field["entry"].get() 
        for field in contestFields
        if field["name"] not in subcontestNames
    }
    subcontest = {
        field["name"]: field["entry"].get()
        for field in contestFields
        if field["name"] in subcontestNames
    }
    subcontest["name"] = subcontest["subcontest_name"]
    del subcontest["subcontest_name"]
    subcontest["class_range_name"], *subcontest["class_range"] = re.split(r"[ ,]", subcontest["class_range"])
    contest["subcontests"] = [subcontest]

    rows = iter(currentGrid)
    header = next(rows)
    subcontest["columns"] = [field["text"] for i,field in enumerate(header) if i not in sc]
    subcontest["contestants"] = []
    for row in rows:
        contestant = {"fields": []}
        for ci, field in enumerate(row):
            text = field["text"].strip() or None
            if ci in sc:
               contestant[sc[ci]] = field["text"]
            else:
                contestant["fields"].append(field["text"])
        contestant["instructors"] = [x.strip() for x in re.split(r"[|,]", contestant["instructors"]) if x.strip() != ""]
        
        subcontest["contestants"].append(contestant)
    
    importoly.addContest(contest)

# interface
root = tk.Tk()
defaultColor = root.cget("bg")

# toolbar
toolbar = tk.Frame(root)
toolbar.pack(fill=tk.X, side=tk.TOP)
openButton = tk.Button(toolbar, text="Open", command=openFile)
openButton.pack()
importButton = tk.Button(toolbar, text="Import", command=importTable)
importButton.pack()

# contest info
contestInfo = tk.Frame(root)
contestInfo.pack(fill=tk.X, after=toolbar)

for ci, cf in enumerate(contestFields):
    tk.Label(contestInfo, text=cf["display"]).grid(row=0, column=ci)
    e = tk.Entry(contestInfo)
    e.grid(row=1, column=ci)
    cf["entry"] = e
    l = tk.IntVar()
    cf["lock"] = l
    ch = tk.Checkbutton(contestInfo, text="Lock", variable=l)
    ch.grid(row=2, column=ci)

# editor
editor = tk.Frame(root)
editor.pack(fill=tk.X, after=contestInfo)

editField = tk.Entry(editor)
editField.grid(row=0, column=0)

def applyEdit(*_):
    if selectedField is not None:
        currentGrid[selectedField[0]][selectedField[1]].configure(text=editField.get())
editField.bind("<Return>", applyEdit)

for ci, sc in enumerate(specialColumns, 1):
    sc["coli"] = None
    def createAction(sc):
        def action(*_):
            if selectedField is not None:
                sc["coli"] = selectedField[1]
                highlightGrid()
        return action

    b = tk.Button(editor, text=f'Set "{sc["name"]}"', command=createAction(sc), background=sc["color"])
    b.grid(row=0, column=ci)

# grid
gridWrapper = ScrollableFrame(root)
gridWrapper.pack(fill=tk.BOTH, expand=1, after=editor, side=tk.LEFT)

gridScrollY = tk.Scrollbar(root, orient=tk.VERTICAL)
gridScrollY.pack(fill=tk.Y, side=tk.RIGHT)
gridWrapper.setYScrollbar(gridScrollY)

currentGrid = []

openFile()
tk.mainloop()

