import rhinoscriptsyntax as rs
import random

filter = "Text File (*.txt)|*.txt|All Files (*.*)|*.*||"
fName = rs.OpenFileName("Save point coordinates as", filter)
f = open(fName, 'rwv')
comp = rs.GetObject("select component", 32)
op = rs.GetPoint("select origin point")
dp = rs.GetPoint("select aim point")
up = rs.GetPoint("select up point")

oList = []
oList.append(op)
oList.append(dp)
oList.append(up)
lines = f.readlines()
rs.EnableRedraw(False)
for i in range(len(lines)):
    ptInfo = lines[i].split('/')
    #print ptInfo
    p = ptInfo[0].split(',')
    d = ptInfo[1].split(',')
    u = ptInfo[2].split(',')
    
    p1 = [float(p[0]), float(p[1]), float(p[2])]
    d1 = [float(d[0]), float(d[1]), float(d[2])]
    u1 = [float(u[0]), float(u[1]), float(u[2])]
    sc = rs.VectorLength(d1)
    d1 = rs.VectorUnitize(d1)
    u1 = rs.VectorUnitize(u1)
    dis = rs.Distance(d1, u1)
    if dis > 0 and dis < 2:
        d1 = rs.VectorAdd(p1, d1)
        u1 = rs.VectorAdd(p1, u1)
        if rs.Distance(d1,p1) > 0 and rs.Distance(u1, p1) > 0:
            tList = [p1,d1,u1]    
            #print tList        
            obj = rs.ScaleObject(comp,[0,0,0],[sc,sc,sc], True )
            rs.OrientObject(obj,oList,tList)
    
        


rs.EnableRedraw(True)
f.close()