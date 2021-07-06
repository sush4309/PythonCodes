import rhinoscriptsyntax as rs

globalScale = 2 #same as hSize

filter = "Text File (*.txt)|*.txt|All Files (*.*)|*.*||"
fName = rs.OpenFileName("Open your text file", filter)
f = open(fName, 'r')

zComp = rs.GetObjects("select zero connect",4)
oneComp = rs.GetObjects("select one connect",4)
straightComp = rs.GetObjects("select straight connect",4)
LComp = rs.GetObjects("select L connect", 4)
threeComp = rs.GetObjects("select three connect",4)
fourComp = rs.GetObjects("select four connect",4)
compList = [zComp,oneComp,straightComp,LComp,threeComp,fourComp]


lines = f.readlines()
origin = [0,0,0]
forward = [0,1,0]
up = [0,0,1]
ref = [origin,forward,up]

for i in range(len(lines)):
    pt = lines[i].split(',')
    x1 = float(pt[0])
    y1 = float(pt[1])
    z1 = float(pt[2])
    x2 = float(pt[3])
    y2 = float(pt[4])
    z2 = float(pt[5])
    type = int(pt[6])
    #if type != 6:
    pos = rs.CreateVector([x1,y1,z1])
    forward = rs.CreateVector([x2,y2,z2])
    forward = rs.VectorAdd(pos,forward)
    up1 = rs.CreateVector([0,0,1])
    up1 = rs.VectorAdd(pos,up1)
    target = [pos,forward,up1]
    
    obj = rs.CopyObjects(compList[type-1])
    for o in obj:
        o = rs.ScaleObject(o,[0,0,0],[globalScale,globalScale,globalScale])
        rs.OrientObject(o,ref,target)

