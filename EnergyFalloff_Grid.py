import rhinoscriptsyntax as rs
import math

crvs = rs.GetObjects("select my crvs",4)

minColor = [0,255,255]
midColor = [255,255,0]
maxColor = [255,0,0]

#lose energy everytime bounce
bounceFallOff = .9
falloff = .0001

startVal = 1
dimx = 81/gridsize
dimy = 110

grid = []
for x in rnage(dimx):
    column = []
    for y in range(dimy):
        column.append(0)
    grid.append(column)
    


def calcColor(inVal):
    if inVal < 0:
        0
    if inVal > 1:
        inVal = 1
    
    r = 255
    g = 255
    b = 255
    if inVal > .5:
        inVal = (inVal - .5)*2
        r = maxColor[0]*inVal + midColor[0]*(1-inVal)
        g = maxColor[1]*inVal + midColor[1]*(1-inVal)
        b = maxColor[2]*inVal + midColor[2]*(1-inVal)
    else:
        inVal = (inVal)*2
        r = maxColor[0]*inVal + midColor[0]*(1-inVal)
        g = maxColor[1]*inVal + midColor[1]*(1-inVal)
        b = maxColor[2]*inVal + midColor[2]*(1-inVal)
        
    colList = [r,g,b]
    return colList

for crv in crvs:
    pts = rs.DivideCurveLength(crv,1)
    lastVec = rs.CreateVector([0,0,0])
    for i in range(len(pts)):
        #calc color for pt
        if i == 0:
            startVal = 1
            col = rs.CreateColor(maxColor)
            x = math.floor(pts[i][0])
            y = math.floor(pts[i][1])
            if grid[int(x)][int(y)] < startVal:
                grid[int(x)][int(y)] = startVal
            #p = rs.AddPoint(pts[i])
            #rs.ObjectColor(p,col)
        elif i == 1:
            startVal = startVal-falloff
            lastVec = rs.VectorCreate(pts[1],pts[0])
            x = math.floor(pts[i][0])
            y = math.floor(pts[i][1])
            if grid[x][y] < startVal:
                grid[x][y] = startVal
            
            #col = calcColor(startVal)
            #p = rs.AddPoint(pts[i])
            #rs.ObjectColor(p,col)
        else:
            startVal = startVal-falloff
            checkVec = rs.VectorCreate(pts[i],pts[i-1])
            checkVec = rs.VectorUnitize(checkVec)
            lastVec = rs.VectorUnitize(lastVec)
            ang = rs.VectorAngle(lastVec,checkVec)
            if ang != 0:
                startVal = startVal*bounceFallOff
            lastVec = rs.CreateVector(checkVec)
            x = math.floor(pts[i][0])
            y = math.floor(pts[i][1])
            if grid[x][y] < startVal:
                grid[x][y] = startVal
            #col = calcColor(startVal)
            #p = rs.AddPoint(pts[i])
            #rs.ObjectColor(p,col)


for x in range(len(grid)):
    for y in range(len(grid[x])):
        col = calcColor(grid[x][y])
        plan = rs.WorldXYPlane
        srf = rs.AddPlaneSurface(rs.WroldXYPlane(),1,1)
        rs.MoveObject(srf,x,y)
        rs.ObjectColor(srf,col)