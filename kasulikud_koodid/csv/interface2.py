import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from tkinter import messagebox as tkmsg
import re
import csv
import copy
import logging
import importoly

contestFields = [
    {"name": "name", "display": "Contest name"},
    {"name": "subject", "display": "Subject"},
    {"name": "type", "display": "Type"},
    {"name": "year", "display": "Year"},
    {"name": "subcontest_name", "display": "Subcontest name"},
    {"name": "class_range", "display": "Class range"},
    {"name": "description", "display": "Description"},
]

subcontestNames = {"subcontest_name", "class_range", "description"}

specialColumns = [
    {"name": "placement", "color": "#dd3030"},
    {"name": "name", "color": "#30dd30"},
    {"name": "first name", "color": "#00aa00"},
    {"name": "last name", "color": "#10aa90"},
    {"name": "class", "color": "#7070dd"},
    {"name": "school", "color": "#41a5fc"},
    {"name": "instructors", "color": "#f78a2f"},
    {"name": "total", "color": "#ffcc00"}
]

inferContest = {
    "subject": [
        {"pattern": "efo|fyysika|füüsika|fys", "value": "Füüsika"},
        {"pattern": "emo|mat|lvs|lvt", "value": "Matemaatika"},
        {"pattern": "eko|keemia", "value": "Keemia"},
        {"pattern": "inf", "value": "Informaatika"},
        {"pattern": "ego", "value": "Geograafia"},
        {"pattern": "ebo", "value": "Bioloogia"},
    ],
    "type": [
        {"pattern": "lv[0-9st]", "value": "Lahtine"},
        {"pattern": "lv", "value": "Lõppvoor"},
        {"pattern": "lah", "value": "Lahtine"},
    ],
    "class_range": [
        {"pattern": "(^|[^1-9])6k", "value": "6,6,6"},
        {"pattern": "(^|[^1-9])7k", "value": "7,7,7"},
        {"pattern": "(^|[^1-9])8k", "value": "8,8,8"},
        {"pattern": "(^|[^1-9])9k", "value": "9,9,9"},
        {"pattern": "10k", "value": "10,10,10"},
        {"pattern": "11k", "value": "11,11,11"},
        {"pattern": "12k", "value": "12,12,12"},
        {"pattern": "(^|[-_ ])g($|[-_.])", "value": "gümnaasium,10,12"},
        {"pattern": "(^|[-_ ])pk?($|[-_.])", "value": "põhikool,8,9"},
        {"pattern": "(^|[-_ ])v($|[-_.])", "value": "vanem,11,12"},
        {"pattern": "(^|[-_ ])n($|[-_.])", "value": "noorem,9,10"},
    ]
}

inferColumns = [
    {"pattern": r"(jrk|koht)\.?", "value": "placement"},
    {"pattern": r".*eesnimi", "value": "first name"},
    {"pattern": r".*pere(konna)?nimi", "value": "last name"},
    {"pattern": r"(õpilane|(õpilase )?nimi)\.?", "value": "name"},
    {"pattern": r"kool\.?", "value": "school"},
    {"pattern": r"kl(ass)?\.?", "value": "class"},
    {"pattern": r".*(juhendajad?|õp(etaja)?).*", "value": "instructors"},
    {"pattern": r".*kokku.*", "value": "total"},
]

deleteColumnColor = "#ffaaaa"


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

def clearGrid(clearSpecial=True):
    global selectedField

    for row in currentGrid:
        for field in row:
            field.destroy()
    currentGrid.clear()
    for field in gridHeader:
        field.destroy()
    gridHeader.clear()
    selectedField = None

    if clearSpecial:
        for sc in specialColumns:
            sc["coli"] = None

def deleteColumnAction(ci):
    def action(*_):
        # Delete the column
        grid = getGrid()
        for row in grid:
            del row[ci]

        setGrid(grid, False)

        # Update the special columns
        for sc in specialColumns:
            if sc["coli"] is None:
                pass
            elif sc["coli"] == ci:
                sc["coli"] = None
            elif sc["coli"] > ci:
                sc["coli"] -= 1
        highlightGrid()

    return action

"""
Set the grid to a 2D list of values
"""
def setGrid(grid, clearSpecial=True):
    clearGrid(clearSpecial)

    if len(grid) == 0:
        return

    for ri, row in enumerate(grid):
        newRow = []
        currentGrid.append(newRow)
        for ci, field in enumerate(row):
            e = tk.Button(gridWrapper, text=field, command=fieldButton(ri, ci))
            e.grid(row=ri+1, column=ci, sticky="nsew")
            newRow.append(e)

    for ci in range(len(grid[0])):
        h = tk.Button(gridWrapper, text="Delete", command=deleteColumnAction(ci), background=deleteColumnColor)
        h.grid(row=0, column=ci)
        gridHeader.append(h)

"""
Get the grid as a 2D list of values
"""
def getGrid():
    grid = []
    for row in currentGrid:
        grid.append([])
        for v in row:
            grid[-1].append(v["text"])

    return grid

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

lastOpenedFile = None
"""
"Open file" action performed
"""
def openFile():
    global lastOpenedFile
    # file dialog
    filename = askopenfilename(filetypes=[("CSV",".csv"), ("File", "*")])
    if filename == ():
        # cancelled
        return

    lastOpenedFile = filename
    reopenFile()

def reopenFile():
    print(lastOpenedFile)
    with open(lastOpenedFile) as inFile:
        parseCSV(inFile)

    inferFields(lastOpenedFile)
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
    if any(field["entry"].get() == "" for field in contestFields if field["name"] != "description"):
        warn("Missing contest information")
        return

    sc = {col["coli"]: col["name"] for col in specialColumns if col["coli"] is not None}
    coli = {col["name"]: col["coli"] for col in specialColumns}

    if coli["placement"] is None:
        warn("Missing placement")
        return

    haveName, haveFirstName, haveLastName = (coli[x] is not None
                                             for x in ("name", "first name", "last name"))
    if haveName:
        if haveFirstName or haveLastName:
            warn("Extra name columns")
            return
    elif not (haveFirstName and haveLastName):
        warn("No name columns")
        return

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

    grid = getGrid()
    rows = iter(grid)
    header = next(rows)
    subcontest["columns"] = [field for i,field in enumerate(header) if i not in sc or sc[i] == "total"]
    subcontest["contestants"] = []
    for row in rows:
        contestant = {"fields": []}
        for ci, field in enumerate(row):
            if ci not in sc or sc[ci] == "total":
                contestant["fields"].append(field.strip())

        contestant["instructors"] = ([] if coli["instructors"] is None else
                                     [x.strip() for x in re.split(r"[|,/]+", row[coli["instructors"]])
                                      if x.strip() != ""])
        contestant["placement"] = re.sub(r"[. ]", "", row[coli["placement"]])
        contestant["class"] = None if coli["class"] is None else row[coli["class"]].strip()
        contestant["school"] = None if coli["school"] is None else row[coli["school"]].strip()

        # Name
        if haveName:
            nameParts = re.split(r"[, ]+", row[specialColumnsN["name"]["coli"]])
        else:
            nameParts = [row[specialColumnsN["first name"]["coli"]], row[specialColumnsN["last name"]["coli"]]]

        nameParts = [part.strip() for part in nameParts if part.strip() != ""]

        if haveName and nameOrderRev.get():
            last = nameParts[0]
            del nameParts[0]
            nameParts.append(last)

        contestant["name"] = " ".join(nameParts)


        subcontest["contestants"].append(contestant)

    importoly.addContest(contest)

# interface
root = tk.Tk()
defaultColor = root.cget("bg")

# toolbar
toolbar = tk.Frame(root)
toolbar.pack(fill=tk.X, side=tk.TOP)
openButton = tk.Button(toolbar, text="Open", command=openFile)
openButton.pack(side='left')
reloadButton = tk.Button(toolbar, text="Reload", command=reopenFile)
reloadButton.pack(side='left')
importButton = tk.Button(toolbar, text="Import", command=importTable)
importButton.pack(side='left')

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

specialColumnsN = {sc["name"]: sc for sc in specialColumns}

for ci, sc in enumerate(specialColumns, 1):
    sc["coli"] = None
    sc["ci"] = ci
    def createAction(sc):
        def action(*_):
            if selectedField is not None:
                sc["coli"] = selectedField[1]
                highlightGrid()
        return action

    def clearAction(sc):
        def action(*_):
            sc["coli"] = None
            highlightGrid()
        return action

    b = tk.Button(editor, text=f'Set "{sc["name"]}"', command=createAction(sc), background=sc["color"])
    b.grid(row=0, column=ci)
    b2 = tk.Button(editor, text=f'Clear', command=clearAction(sc), background=sc["color"])
    b2.grid(row=1, column=ci)

# Extra widgets
def genPlacementAction(*_):
    total = specialColumnsN["total"]["coli"]
    if total is not None:
        placement = specialColumnsN["placement"]["coli"]
        if placement is None:
            # Create the placement column
            grid = getGrid()
            rows = iter(grid)
            header = next(rows)
            header.insert(0, "Koht")
            for row in rows:
                row.insert(0, "0")

            setGrid(grid, False)

            # Increment the indices
            for sc in specialColumns:
                if sc["coli"] is not None:
                    sc["coli"] += 1

            specialColumnsN["placement"]["coli"] = 0
            placement = 0
            total = specialColumnsN["total"]["coli"]
            highlightGrid()

        # Calculate the placement
        lastS = float("inf")
        currPlace = 0
        startPlace = 0

        rows = iter(currentGrid)
        # Skip the header
        next(rows)
        for row in rows:
            s = float(row[total]["text"].replace(",", ".").replace('%',''))
            currPlace += 1
            if s < lastS:
                row[placement].configure(text=str(currPlace))
                lastS = s
                startPlace = currPlace
            else:
                row[placement].configure(text=str(startPlace))
genPlacementButton = tk.Button(editor, text='From "total"', command=genPlacementAction, background=specialColumnsN["placement"]["color"])
genPlacementButton.grid(row=2, column=specialColumnsN["placement"]["ci"])

nameOrderRev = tk.IntVar()
nameOrderRevCheck = tk.Checkbutton(editor, text="Reversed name", variable=nameOrderRev)
nameOrderRevCheck.grid(row=2, column=specialColumnsN["name"]["ci"])

# grid
gridWrapper = ScrollableFrame(root)
gridWrapper.pack(fill=tk.BOTH, expand=1, after=editor, side=tk.LEFT)

gridScrollY = tk.Scrollbar(root, orient=tk.VERTICAL)
gridScrollY.pack(fill=tk.Y, side=tk.RIGHT)
gridWrapper.setYScrollbar(gridScrollY)

currentGrid = []
gridHeader = []

openFile()
tk.mainloop()
