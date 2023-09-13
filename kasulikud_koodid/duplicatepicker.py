from tkinter import *
import os
import json
from itertools import chain

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info('Running!')

import mysql.connector

with open(os.path.join(os.path.dirname(__file__),"credentials.json")) as f:
    config = json.loads(f.read())
mysql_user = config["user"]
mysql_passwd = config["password"]
mysql_db = config["database"]
mysql_host = config["host"]
conn = mysql.connector.connect(user=mysql_user, password=mysql_passwd, database=mysql_db, host=mysql_host)
cur = conn.cursor()

#font = ("Ubuntu Mono", 12, "")
font = "TkFixedFont"

currData = []
searchMap = []
maxL = [0, 0, 0]

def getAll():
    global maxL
    query = "SELECT id, name, UPPER(REGEXP_REPLACE(name, '[^[:alnum:]]+', '|')) subname FROM person ORDER BY subname"
    logging.info('Query: ' + repr(query))
    cur.execute(query)
    currData.clear()
    maxL = [0, 0, 0]
    for id, name, subname in cur:
        currData.append((id, name, subname))
        for i, s in enumerate((str(id), name, subname)):
            maxL[i] = max(maxL[i], len(s))
    
    for id, name, subname in currData:
        id, name, subname = (str(a).ljust(l) for a, l in zip((id, name, subname), maxL))
        s = f'{id}    {name}    {subname}'
        chooseBox.insert(END, s)
        destBox.insert(END, s)

    searchMap.clear()
    chooseBox.selection_clear(0, END)
    destBox.selection_clear(0, END)
    doSearch()

def message(text):
    popup = Toplevel(master)
    popup.wm_title("Message")
    popup.geometry('+800+500')
    
    label = Label(popup, text=text)
    label.pack(side=TOP, fill=X, pady=10)
    
    def okCallback():
        popup.grab_release()
        popup.destroy()
    
    button = Button(popup, text='OK', command=okCallback)
    button.pack(side=BOTTOM, fill=X)
    
def replacePeople():
    try:
        replacement = currData[searchMap[next(i for i in destBox.curselection())]]
    except StopIteration:
        return

    people = [currData[searchMap[i]] for i in chooseBox.curselection() if currData[searchMap[i]] != replacement]
    if len(people) == 0:
        return
    
    logging.debug(f'people: {people}, replacement: {replacement}')

    try:
        query = 'UPDATE contestant SET person_id = %s WHERE person_id IN (' + ', '.join('%s' for _ in people) + ')'
        t = tuple(map(str, chain([replacement[0]], (p[0] for p in people))))
        logging.debug('Query: ' + repr(query) + ', ' + repr(t))
        cur.execute(query, t)
        logging.debug('Affected: ' + str(cur.rowcount))
        
        query = 'UPDATE mentor SET mentor_id = %s WHERE mentor_id IN (' + ', '.join('%s' for _ in people) + ')'
        logging.debug('Query: ' + repr(query) + ', ' + repr(t))
        cur.execute(query, t)
        logging.debug('Affected: ' + str(cur.rowcount))
        
        query = 'DELETE FROM person WHERE id in (' + ', '.join('%s' for _ in people) + ')'
        t = tuple(str(p[0]) for p in people)
        logging.debug('Query: ' + repr(query) + ', ' + repr(t))
        cur.execute(query, t)
        logging.debug('Affected: ' + str(cur.rowcount))
        
        conn.commit()
        
        getAll()
    except Exception as e:
        conn.rollback()
        logging.exception('Exception when replacing:')
        message("Exception when replacing:\n" + str(e))

def confirm(text, callback):
    popup = Toplevel(master)
    popup.wm_title("Confirm")
    popup.geometry('+800+500')
    
    label = Label(popup, text=text)
    label.pack(side=TOP, fill=X, pady=10)

    buttonFrame = Frame(popup)
    buttonFrame.pack(side=BOTTOM, fill=X)
    
    def yesCallback():
        popup.grab_release()
        popup.destroy()
        callback()
    
    yesButton = Button(buttonFrame, text="Yes", command=yesCallback)
    yesButton.grid(row=0, column=0)

    def noCallback():
        popup.grab_release()
        popup.destroy()

    noButton = Button(buttonFrame, text="No", command=noCallback)
    noButton.grid(row=0, column=1)

    buttonFrame.columnconfigure(0, weight=1)
    buttonFrame.columnconfigure(1, weight=1)
    buttonFrame.rowconfigure(0, weight=1)
    
    popup.grab_set()

def doSearch(*_):
    global searchMap
    s = searchBox.get().upper()
    logging.debug(repr(s))

    selectedL = set(searchMap[i] for i in chooseBox.curselection())
    selectedR = set(searchMap[i] for i in destBox.curselection())
    searchMap = [i for i, p in enumerate(currData) if i in selectedL or i in selectedR or s in str(p[0]) or s in p[1].upper()]

    chooseBox.delete(0, END)
    destBox.delete(0, END)
    
    for i in searchMap:
        t = currData[i]
        id, name, subname = (str(a).ljust(l) for a, l in zip(t, maxL))
        s = f'{id}    {name}    {subname}'
        chooseBox.insert(END, s)
        destBox.insert(END, s)
        if i in selectedL:
            chooseBox.selection_set(END)
        if i in selectedR:
            destBox.selection_set(END)
    
    
master = Tk()

master.geometry('1200x800+400+200')

chooseFrame = Frame(master)
chooseFrame.grid(row=0, column=0, sticky=N+S+E+W)

##############################################################

chooseBoxFrame = LabelFrame(chooseFrame, text='Choose')
chooseBoxFrame.grid(row=0, column=0, sticky=N+S+E+W)

destBoxFrame = LabelFrame(chooseFrame, text='Replacement')
destBoxFrame.grid(row=0, column=1, sticky=N+S+E+W)

chooseBox = Listbox(chooseBoxFrame, selectmode=EXTENDED, exportselection=0)
chooseBox.grid(row=0, column=0, sticky=N+S+E+W)
chooseBox.configure(font=font)

destBox = Listbox(destBoxFrame, exportselection=0)
destBox.grid(row=0, column=0, sticky=N+S+E+W)
destBox.configure(font=font)

chooseBoxFrame.columnconfigure(0, weight=1)
chooseBoxFrame.rowconfigure(0, weight=1)
destBoxFrame.columnconfigure(0, weight=1)
destBoxFrame.rowconfigure(0, weight=1)

chooseScrollbar = Scrollbar(chooseFrame, orient="vertical")

def scrollFromBar(*args):
    chooseBox.yview(*args)
    destBox.yview(*args)

def scrollFromBox(*args):
    chooseScrollbar.set(*args)
    chooseBox.yview_moveto(args[0])
    destBox.yview_moveto(args[0])
    
chooseScrollbar.config(command=scrollFromBar)
chooseScrollbar.grid(row=0, column=3, sticky=N+S)
chooseBox.config(yscrollcommand=scrollFromBox)
destBox.config(yscrollcommand=scrollFromBox)

##############################################################

chooseFrame.columnconfigure(0, weight=1, uniform="group1")
chooseFrame.columnconfigure(1, weight=1, uniform="group1")
chooseFrame.columnconfigure(2, weight=0)
chooseFrame.rowconfigure(0, weight=1)

buttonFrame = Frame(master)
buttonFrame.grid(row=1, column=0, sticky=E+W)

queryAll = Button(buttonFrame, text="Query all", command=getAll)
queryAll.grid(row=0, column=0)

def replaceCommand():
    count = len(chooseBox.curselection())
    confirm(f'Are you sure?\nReplacing {count} row' + ('' if count == 1 else 's') + '.', replacePeople)

replaceButton = Button(buttonFrame, text="Replace", command=replaceCommand)
replaceButton.grid(row=0, column=1)

searchVar = StringVar()
searchVar.trace_add("write", doSearch)

searchBox = Entry(buttonFrame, textvariable=searchVar)
searchBox.grid(row=0, column=2, sticky=E+W)

buttonFrame.columnconfigure(0, weight=0)
buttonFrame.columnconfigure(1, weight=0)
buttonFrame.columnconfigure(2, weight=1)
buttonFrame.rowconfigure(0, weight=1)

master.columnconfigure(0, weight=1)
master.rowconfigure(0, weight=1)
master.rowconfigure(1, weight=0)

getAll()

mainloop()
