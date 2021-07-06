import rhinoscriptsyntax as rs

filter = "Text File (*.txt)|*.txt|All Files (*.*)|*.*||"
fName = rs.OpenFileName("Open your text file", filter)
f = open(fName, 'r')

comp = rs.GetObject("select your box", 32)
lines = f.readlines()

boxSize = 8

for i in range(len(lines)):
    pt = lines[i].split(',')
    x1 = float(pt[0])
    y1 = float(pt[1])
    z1 = float(pt[2])
    r = float(pt[3])
    g = float(pt[4])
    b = float(pt[5])
    
    box= rs.CopyObject(comp)
    box= rs.ScaleObject(box,[0,0,0],[boxSize,boxSize,boxSize])
    box = rs.MoveObject(box,[x1,y1,z1])
    rs.ObjectColor(box,[r,g,b])
    
    
    
    
