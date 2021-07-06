import rhinoscriptsyntax as rs
import random

filter = "Text File (*.txt)|*.txt|All Files (*.*)|*.*||"
fName = rs.SaveFileName("Save point coordinates as", filter)
f = open(fName, 'w')
ptCloud = rs.GetObjects("select your pointCloud",rs.filter.pointcloud)

colors = rs.PointCloudPointColors(ptCloud)

points = rs.PointCloudPoints(ptCloud)

for i in range(len(points)):
    
    pos = points[i]
    r = rs.ColorRedValue(colors[i])
    g = rs.ColorGreenValue(colors[i])
    b = rs.ColorBlueValue(colors[i])
    f.write(str(pos)+ ","+str(r) + "," + str(g) +","+str(b)+"\n")
print("I'm done")




f.close()