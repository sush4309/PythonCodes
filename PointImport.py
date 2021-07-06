import rhinoscriptsyntax as rs

filter = "Text File (*.txt)|*.txt|All Files (*.*)|*.*||"
fName = rs.OpenFileName("Open your text file", filter)
f = open(fName, 'r')

lines = f.readlines()

for i in range(len(lines)):
    pt = lines[i].split(',')
    x1 = float(pt[0])
    y1 = float(pt[1])
    z1 = float(pt[2])
    
    
    lin = rs.AddPoint([x1,y1,z1])
    
