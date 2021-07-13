import rhinoscriptsyntax as rs

crvs = rs.GetObjects("select my crvs",4)

minColor = [0,255,255]
maxColor = [255,0,0]

#lose energy everytime bounce
bounceFallOff = .9
falloff = -.0001

startVal = 1

def calcColor(inVal):
    if inVal < 0:
        0
    r = maxColor[0]*inVal + minColor[0]*(1-inVal)
    g = maxColor[1]*inVal + minColor[1]*(1-inVal)
    b = maxColor[2]*inVal + minColor[2]*(1-inVal)
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
            p = rs.AddPoint(pts[i])
            rs.ObjectColor(p,col)
        elif i == 1:
            startVal = startVal-falloff
            lastVec = rs.VectorCreate(pts[1],pts[0])
            col = calcColor(startVal)
            p = rs.AddPoint(pts[i])
            rs.ObjectColor(p,col)
        else:
            startVal = startVal-falloff
            checkVec = rs.VectorCreate(pts[i],pts[i-1])
            checkVec = rs.VectorUnitize(checkVec)
            lastVec = rs.VectorUnitize(lastVec)
            ang = rs.VectorAngle(lastVec,checkVec)
            if ang != 0:
                startVal = startVal*bounceFallOff
            lastVec = rs.CreateVector(checkVec)
            col = calcColor(startVal)
            p = rs.AddPoint(pts[i])
            rs.ObjectColor(p,col)


