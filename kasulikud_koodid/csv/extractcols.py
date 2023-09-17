
import argparse
import pickle
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextLineHorizontal, LTChar
from typing import Iterable
import pdf2image
import cv2
import numpy as np
import csv
import sys

LINE_WIDTH = 1

parser = argparse.ArgumentParser()
parser.add_argument("pdf")
parser.add_argument("csv", nargs="?", default=None)

args = parser.parse_args()

if args.csv is None:
    args.csv = args.pdf.removesuffix(".pdf") + ".csv"

pages = extract_pages(args.pdf)

images = pdf2image.convert_from_path(args.pdf)
try:
    with open("lastboxes.pickle",'rb') as f:
        prev = pickle.loads(f.read())
except:
    prev = ([], [])

def get_texts(root):
    if isinstance(root, LTTextLineHorizontal):
        yield root
        return
    if isinstance(root, Iterable):
        for el in root:
            yield from get_texts(el)

def box_to_image(box):
    x1, y1, x2, y2 = map(round, (box[0] * scx, ih - box[1] * scy, box[2] * scx, ih - box[3] * scy))
    return (x1, y1), (x2, y2)

def reorder(r):
    p1 = min(r[0][0], r[1][0]), min(r[0][1], r[1][1])
    p2 = max(r[0][0], r[1][0]), max(r[0][1], r[1][1])
    return (p1, p2)

def overlap_lin(a, b):
    return max(0, min(a[1], b[1]) - max(a[0], b[0]) + 1)

def overlap(r1, r2):
    r1 = reorder(r1)
    r2 = reorder(r2)
    x = overlap_lin((r1[0][0], r1[1][0]), (r2[0][0], r2[1][0]))
    y = overlap_lin((r1[0][1], r1[1][1]), (r2[0][1], r2[1][1]))
    return x, y

def dims(r):
    r = reorder(r)
    return (r[1][0] - r[0][0] + 1, r[1][1] - r[0][1] + 1)

cols = []
rowCount = 0
prevs = ([], [])

for p, img in zip(pages, images):
    print(p)
    img = np.array(img)
    f = min(1800 / img.shape[1], 1000 / img.shape[0])
    base_img = cv2.resize(img, None, fx=f, fy=f)
    del img

    iw = base_img.shape[1]
    ih = base_img.shape[0]
    
    pw = p.bbox[2]
    ph = p.bbox[3]

    scx = iw / pw
    scy = ih / ph
    
    boxes = []
    for tb in get_texts(p):
        box = tb.bbox
        box = box_to_image(box)
        boxes.append(([ch for ch in tb if isinstance(ch, LTChar)], box))

    boxes.sort(key=lambda x: x[1][0][1])
        
    selectBoxes = []
    removeBoxes = []
    currStart = None
    currPos = None
    removing = False
    altAddMode = False
    cv2.namedWindow("page")
    def mouse(event, x, y, flags, _):
        global currStart, currPos

        currPos = (x, y)
        if altAddMode:
            boxlist = removeBoxes if removing else selectBoxes
            if boxlist:
                last = boxlist[-1]
                last_endx = last[1][0]
                last_starty = last[0][1]
                last_endy = last[1][1]
                currStart = (last_endx, last_starty)
                currPos = (x, last_endy)
            else:
                # not the best default but better than crashing
                currStart = (0, 0)
                currPos = (x, y)
        
        if event == cv2.EVENT_LBUTTONDOWN and not altAddMode:
            currStart = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            if removing:
                removeBoxes.append((currStart, currPos))
            else:
                selectBoxes.append((currStart, currPos))
            currStart = None
            
    cv2.setMouseCallback("page", mouse)
    
    while True:
        img = base_img.copy()

        checkBox = None
        if currStart is not None:
            checkBox = (currStart, currPos)
        elif len(selectBoxes) > 0:
            checkBox = selectBoxes[-1]
            
        for _, box in boxes:
            col = (0, 0, 255)
            lw = LINE_WIDTH
            if checkBox is not None:
                o = overlap(checkBox, box)
                if o == dims(box):
                    col = (0, 255, 0)
                elif min(o) > 0:
                    col = (0, 255, 255)

            for rb in removeBoxes:
                if min(overlap(rb, box)) > 0:
                    lw = -lw
                    col = (0, 0, 0)
                    break
            
            cv2.rectangle(img, box[0], box[1], col, lw)

        if selectBoxes:
            # highlight the first one as it's used for row detection
            cv2.rectangle(img, selectBoxes[0][0], selectBoxes[0][1], (255, 200, 0), LINE_WIDTH)
        for box in selectBoxes[1:]:
            cv2.rectangle(img, box[0], box[1], (255, 0, 0), LINE_WIDTH)
            
        if checkBox is not None:
            col = (255, 0, 255)
            if removing:
                col = (100, 0, 100)
            cv2.rectangle(img, checkBox[0], checkBox[1], col, LINE_WIDTH)
        cv2.imshow("page", img)
        key = cv2.waitKey(100) & 0xff

        if cv2.getWindowProperty("page", cv2.WND_PROP_VISIBLE) < 1 or key == ord('q'):
            sys.exit(1)
        elif key == ord('d'):
            if removing:
                if len(removeBoxes) > 0:
                    removeBoxes.pop()
            else:
                if len(selectBoxes) > 0:
                    selectBoxes.pop()
        elif key == ord('r'):
            removing = not removing
        elif key == ord('w'):
            break
        elif key == ord('x'):
            removeBoxes.clear()
            selectBoxes.clear()
        elif key == ord('p'):
            selectBoxes, removeBoxes = prev
        elif key == ord('f'):
            if removing:
                removeBoxes = removeBoxes[::-1]
            else:
                selectBoxes = selectBoxes[::-1]
        elif key == ord('a'):
            altAddMode = not altAddMode
            currStart = None

    prev = selectBoxes, removeBoxes

    # save here in case the parser crashes or something
    with open("lastboxes.pickle",'wb') as f:
        f.write(pickle.dumps(prev))
            
    #selectBoxes.sort()

    newBoxes = []
    for chars, box in boxes:
        for rb in removeBoxes:
            if min(overlap(box, rb)) > 0:
                break
        else:
            newBoxes.append((chars, box))
    boxes = newBoxes
    
    rc = []
    lineYs = []
    for ci, selectBox in enumerate(selectBoxes):
        if len(cols) == ci:
            cols.append(["" for _ in range(rowCount)])
        rc.append(0)
        for chars, box in boxes:
            if min(overlap(selectBox, box)) > 0:
                s = []
                for ch in chars:
                    cbox = box_to_image(ch.bbox)
                    if overlap(selectBox, cbox) == dims(cbox):
                        s.append(ch.get_text())
                s = "".join(s).strip()
                if len(s) > 0:
                    if ci == 0:
                        lineYs.append(box[0][1])
                        rc[ci] += 1
                        cols[ci].append(s)
                    else:
                        while len(lineYs) > rc[ci] and lineYs[rc[ci]] < box[0][1] - 4:
                            # this box is too far down - there must have been blanks before
                            rc[ci] += 1
                            cols[ci].append("")
                        if len(lineYs) > rc[ci] and box[0][1] < lineYs[rc[ci]] - 4:
                            # this box is too far up - should be a part of the previous value
                            cols[ci][-1] += '\n' + s
                        else:
                            rc[ci] += 1
                            cols[ci].append(s)
    rowCount += max(rc, default=0)
    for col in cols:
        col += ["" for _ in range(rowCount - len(col))]

with open(args.csv, "w", newline="") as f:
    writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for ri in range(rowCount):
        writer.writerow([col[ri] for col in cols])
