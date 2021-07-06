import rhinoscriptsyntax as rs

obj = rs.GetObject("select mesh for terrain",32)
startPts = rs.GetObjects("select pts for start",1)

agentList = []

normals = rs.MeshFaceNormals(obj)

#set the up vector for cross Products
globalUp = rs.CreateVector([0,0,1])

gens = 80
speed = 1

def constrainVec(inVec):
    temp = rs.VectorUnitize(inVec)
    if temp[0] < -.25:
        temp[0] = -1
    elif temp[0] > .25:
        temp[0] = 1
    else:
        temp[0] = 0
        
    if temp[1] < -.25:
        temp[1] = -1
    elif temp[1] > .25:
        temp[1] = 1
    else:
        temp[1] = 0
        
    if temp[2] < -.5:
        temp[2] = -.5
    elif temp[2] > .5:
        temp[2] = .5
    else:
        temp[2] = 0
    return temp

class agent:
    def __init__(self, inPos, inType):
        self.pos = inPos
        self.type = inType
        self.death = True
        self.history = []
       
    
    def update(self):
        acc = [0,0,0]
        #behavior area
        cr = self.slopeTrack()
        st = self.seekTrail()
        mAtt = self.meshAttract()#this is a soft mesh attraction
        #scale behaviors 
        cr = rs.VectorScale(cr,1)
        st = rs.VectorScale(st,.25)
        mAtt = rs.VectorScale(mAtt,.5)
        #add behaviors to acc
        acc = rs.VectorAdd(acc,cr)
        acc = rs.VectorAdd(acc,st)
        acc = rs.VectorAdd(acc,mAtt)
        acc = constrainVec(acc)
        acc = rs.VectorScale(acc,speed)
        self.pos = rs.VectorAdd(self.pos, acc)
        mPt = rs.MeshClosestPoint(obj,self.pos)
        dis = rs.Distance(mPt[0],self.pos)
        if dis > speed:
            self.death = False       
        else:
            #this is a hard snap to the mesh
            #self.pos = mPt[0]
            self.history.append(self.pos)
    
    def meshAttract(self):
        mPt = rs.MeshClosestPoint(obj,self.pos)
        temp = rs.VectorCreate(mPt[0], self.pos)
        #if you want to constrain to a maximum of 1
        if rs.VectorLength(temp) > 1:
            temp = rs.VectorUnitize(temp)
            #temp = rs.VectorScale(temp,2)
        return temp
    
    def seekTrail(self):
        sum = [0,0,0]
        #loop through all the agents and their histories
        for i in range(len(agentList)):
            if agentList[i] != self:
                for j in range(len(agentList[i].history)):
                    p = agentList[i].history[j]
                    dis = rs.Distance(p, self.pos)
                    if dis > speed:
                        factor = 1/dis*dis
                        temp = rs.VectorCreate(p,self.pos)
                        temp = rs.VectorUnitize(temp)
                        temp = rs.VectorScale(temp,factor)
                        sum = rs.VectorAdd(temp,sum)
                    else:
                        self.death = False
        if rs.VectorLength(sum) > 0:
            sum = rs.VectorUnitize(sum)
        return sum
    
    def slopeTrack(self):
        mPt = rs.MeshClosestPoint(obj,self.pos)        
        n = normals[mPt[1]]
        cross = rs.VectorCrossProduct(n,globalUp)
        cross = rs.VectorUnitize(cross)
        if self.type == 0:
            cross = rs.VectorScale(cross,-1)
        return cross
            
    def render(self):
        rs.AddPoint(self.pos)
        


for i in range(len(startPts)):
    loc = rs.PointCoordinates(startPts[i])
    loc[0] = int(loc[0])
    loc[1] = int(loc[1])
    loc[2] = int(loc[2])
    a = agent(loc,0)
    agentList.append(a)
    a = agent(loc,1)
    agentList.append(a)


for i in range(gens):
    for j in range(len(agentList)):
        if agentList[j].death:
            agentList[j].update()
        if agentList[j].death:
            agentList[j].render()
        if i == gens-1:
            if len(agentList[j].history) > 2:
                rs.AddCurve(agentList[j].history, degree=1)





