#
#Kood võtab erinevate klasside tulemused ja lisab kõik ühte koondtabelisse nimede järgi
#

f1  = open("efo63lv08.csv", "r")
f2  = open("efo63lv09.csv", "r")
#f3  = open("efo63lv12.csv", "r")
F  = open("efo63lvPK.csv", "r")

andmed = f1.read()+"\n"+f2.read()#+"\n"+f3.read()
andmed = [x.split(",") for x in andmed.split("\n")]
tul = [x.split(",") for x in F.read().split("\n")]

V= open("efo2016PK.csv", "w")
#V.write(andmed)

c=0
def kokku(i,j):
    out=i[0]+","+i[1]+","+i[2]+","+i[3]+","+i[4]+","
    out+=j[3]+","+j[4]+","+j[5]+","+j[6]+","+j[7]+","+j[8]+","
    out+=j[9]+","+j[10]+","+j[11]+","+j[12]+","+j[13]+","+j[14]+","+j[15]+","
    out+=i[6]
    return out

for i in tul:
    for j in andmed:
        if i[1] == j[1]:
            print(kokku(i,j))
            V.write(kokku(i,j)+"\n")
            c+=1

print(c)

V.close()
