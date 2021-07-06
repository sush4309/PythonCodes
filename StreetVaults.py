import rhinoscriptsyntax as rs

pts = rs.GetObjects("select pts", 1)

minDim = 4

ptLocs = []

for i in range(len(pts)):
    loc = rs.PointCoordinates(pts[i])
    ptLocs.append(loc)

for i in range(len(ptLocs)):
    closDis = 32.0
    closLoc = rs.CreateVector([0,0,0])
    for j in range(len(ptLocs)):
        if ptLocs[j][2] < (ptLocs[i][2]-minDim):
            dis = rs.Distance(ptLocs[j], ptLocs[i])
            if dis < closDis:
                closDis = dis
                closLoc = rs.CreateVector(ptLocs[j])
    if closDis < 32.0:
        midPt = rs.CreateVector([closLoc[0], closLoc[1], ptLocs[i][2]])
        locList = [ptLocs[i],midPt,closLoc]
        rs.AddCurve(locList,2)