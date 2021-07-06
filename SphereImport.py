import rhinoscriptsyntax as rs

filter = "Text File (*.txt)|*.txt|All Files (*.*)|*.*||"
fName = rs.OpenFileName("Open your text file", filter)
f = open(fName, 'r')

#comp = rs.GetObject("select your box", 32)
lines = f.readlines()

boxSize = 8

o = [0,0,0]
f = [0,1,0]
u = [0,0,1]

for i in range(len(lines)):
    pt = lines[i].split(',')
    x1 = float(pt[0])
    y1 = float(pt[1])
    z1 = float(pt[2])
    x2 = float(pt[3])
    y2 = float(pt[4])
    z2 = float(pt[5])
    dirVec = rs.CreateVector([x2,y2,z2])
    r = rs.VectorLength(dirVec)
    #dirVec = rs.VectorUnitize(dirVec)
    
    p = rs.CreateVector([x1,y1,z1])
    dirVec = rs.VectorAdd(dirVec,p)
    rs.AddLine(p,dirVec)
    #pU = rs.CreateVector([0,0,1])
    #pU = rs.VectorAdd(p,pU)
    
    #box= rs.CopyObject(comp)
    #box= rs.ScaleObject(box,[0,0,0],[r,r,r])
    #box = rs.MoveObject(box,[x1,y1,z1])
    #box = rs.OrientObject(box,[o,f,u],[p,dirVec,pU])
    
    
    
    
    
