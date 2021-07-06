import rhinoscriptsyntax as rs
import math
import random

#import our mesh component
mComp = rs.GetObject("select mesh component", 32)
obj = rs.GetObject("select mesh for tracking",32)

startPts =  rs.GetObjects("select starting cells",1)
#import our negative points in our script
negPts = rs.GetObjects("select negative points", 1)
posPts = rs.GetObjects("select positive points", 1)
#rhino has imported guid's and we need to conver them to xyz locations
negLocs = []

speed = .25

if negPts:
    for i in range(len(negPts)):
        #get the vector location for the pt
        loc = rs.PointCoordinates(negPts[i])
        negLocs.append(loc)

posLocs = []
if posPts:
    for i in range(len(posPts)):
        #get the vector location for the pt
        loc = rs.PointCoordinates(posPts[i])
        posLocs.append(loc)

#global variables
gens = 20
dimx = 10
dimy = 10
dimz = 10
agentList = []
origin = [0,0,0]
forward = [0,1,0]
up = [0,0,1]
ref = [origin,forward,up]

norms = rs.MeshFaceNormals(obj)

def meshClosePt(inVec):
    mVals = rs.MeshClosestPoint(obj,inVec)
    return mVals
    

def forceOrtho(inVec):
        # the x componet of inVec is inVec[0] and the y is inVec[1] and x is bigger then z
        #[x,y,z]
       
        if abs(inVec[0]) > abs(inVec[1]) and abs(inVec[0]) > abs(inVec[2]):
            #x is the biggest
            inVec[1] = 0
            inVec[2] = 0
        elif abs(inVec[1]) > abs(inVec[2]):
            #y is the biggest
            inVec[0] = 0
            inVec[2] = 0
        else:
            #z is the biggest
            inVec[0] = 0
            inVec[1] = 0
        temp = rs.VectorUnitize(inVec)
        return temp
        
#a class a collection of variables and functions that can be repeated
#unlike a function no parenthesis


class agent:
    #constructor function is instructions for creating the copy of the class
    # __init__ is a specific name for constructor functions
    #self will get filled automatically
    def __init__(self,inLoc):
        self.pos = inLoc
        self.history = []
        self.history.append(self.pos)
        self.switch = True
    
    def update(self):        
        #setup an empty acceleration function
        acc = [0,0,0]
        #call our behavior functions
        #mag = self.magnet()
        avd = self.avoid()
        coh = self.cohesion()
        mAtt = self.meshAvoid()
        #add behaviors to acc
        #mag = rs.VectorScale(mag,1)
        avd = rs.VectorScale(avd,1)
        coh = rs.VectorScale(coh,1)
        mAtt = rs.VectorScale(mAtt,1)
        #acc = rs.VectorAdd(acc,mag)
        acc = rs.VectorAdd(acc,avd)
        acc = rs.VectorAdd(acc,coh)
        acc = rs.VectorAdd(acc,mAtt)
        acc = rs.VectorUnitize(acc)
        acc = forceOrtho(acc)
        acc = rs.VectorScale(acc,speed)
        #is add acc to self.pos
        self.pos = rs.VectorAdd(self.pos,acc)
        #if you want a hard mesh snap uncomment below
        #mList = meshClosePt(self.pos)
        #self.pos = mList[0]
        self.colCheck()
        #add our position to history
        self.history.append(self.pos)
    
    #check if colliding
    def colCheck(self):
        for i in range(len(agentList)):
            for j in range(len(agentList[i].history)):
                dis = rs.Distance(self.pos, agentList[i].history[j])
                if dis == 0:
                    self.switch = False
    
    def meshAvoid(self):
        mList = meshClosePt(self.pos)
        temp = norms[mList[1]]
        #temp = rs.VectorUnitize(temp)
        return temp
        
    def meshAttract(self):
        mList = meshClosePt(self.pos)
        temp = rs.VectorCreate(mList[0], self.pos)
        #temp = rs.VectorUnitize(temp)
        return temp
        
    def avoid(self):
        #create a zero vector to add all our avoid vectors to
        sum = [0,0,0]
        #loop through every agent in the scene
        for i in range(len(agentList)):
            other = agentList[i]
            if other != self:
                for j in range(len(other.history)):
                    dis = rs.Distance(other.history[j], self.pos)
                    if dis < 1.5*speed and dis > 0:
                        temp = rs.VectorCreate(self.pos,other.history[j])
                        factor = 1/(dis*dis)
                        temp = rs.VectorUnitize(temp)
                        temp = rs.VectorScale(temp,factor)
                        sum = rs.VectorAdd(temp,sum)
        if sum[0] != 0 or sum[1] != 0 or sum[2] != 0:
            sum = rs.VectorUnitize(sum)
        return sum
        
    def cohesion(self):
        #create a zero vector to add all our avoid vectors to
        sum = [0,0,0]
        #loop through every agent in the scene
        for i in range(len(agentList)):
            other = agentList[i]
            if other != self:
                for j in range(len(other.history)):
                    dis = rs.Distance(other.history[j], self.pos)
                    if dis > 1.5*speed and dis < 12*speed:
                        temp = rs.VectorCreate(self.pos,other.history[j])
                        factor = -1/(dis*dis)
                        temp = rs.VectorUnitize(temp)
                        temp = rs.VectorScale(temp,factor)
                        sum = rs.VectorAdd(temp,sum)
        if sum[0] != 0 or sum[1] != 0 or sum[2] != 0:
            sum = rs.VectorUnitize(sum)
        return sum
    #calculate magnet behavior
    def magnet(self):
        #create a zero vector to add all of the vectors to
        sum = [0,0,0]
        #loop through all of the negative pt locations
        for i in range(len(negLocs)):
            #create a vector from the nPt location to our position
            temp = rs.VectorCreate(self.pos,negLocs[i])
            #scale our vector to a length of 1
            temp = rs.VectorUnitize(temp)
            #scale our vector by 1/dis2
            dis = rs.Distance(self.pos, negLocs[i])
            if dis > 0:
                factor = 1/(dis*dis)
                temp = rs.VectorScale(temp,factor)
                #add this vector to sum
                sum = rs.VectorAdd(sum, temp)
        #loop through all of the positive pt locations
        for i in range(len(posLocs)):
            #create a vector from the nPt location to our position
            temp = rs.VectorCreate(self.pos,posLocs[i])
            #scale our vector to a length of 1
            temp = rs.VectorUnitize(temp)
            #scale our vector by 1/dis2
            dis = rs.Distance(self.pos, posLocs[i])
            if dis > 0:
                factor = -1/(dis*dis)
                temp = rs.VectorScale(temp,factor)
                #add this vector to sum
                sum = rs.VectorAdd(sum, temp)
        sum = rs.VectorUnitize(sum)
        return sum
    
    #forceOrtho works in 3D 
    
            
    def render(self):
        if self.switch == True:
            rs.AddPoint(self.pos)

#this loops create the agents at their original positions
for pt in startPts:
    if random.random() < .75:
        loc = rs.PointCoordinates(pt)
        a = agent(loc)
        agentList.append(a)

#the number of times we want the agent to move
for i in range(gens):
    #loop through every agent and move them
    for j in range(len(agentList)):
        #call the update and render for each agent
        if agentList[j].switch:
            agentList[j].update()
            agentList[j].render()
        if i == gens-1:
            if len(agentList[j].history) > 1:
                for k in range(len(agentList[j].history)-1):
                    if agentList[j].history[k][0] != agentList[j].history[k+1][0] or agentList[j].history[k][1] != agentList[j].history[k+1][1] or agentList[j].history[k][2] != agentList[j].history[k+1][2]:
                        #check to see if the next point z value is the same as current point
                        if agentList[j].history[k][2] == agentList[j].history[k+1][2]:
                            #ref = [origin,forward,up]
                            p = agentList[j].history[k]
                            f = agentList[j].history[k+1]
                            u = rs.VectorAdd(p,up)
                            targ = [p,f,u]
                            #targ = [[0,0,0],[0,1,0],[0,0,1]]
                            #targ[1][1]
                            tempComp = rs.CopyObject(mComp)
                            tempComp = rs.ScaleObject(tempComp,[0,0,0],[speed,speed,speed])
                            rs.OrientObject(tempComp,ref,targ)
                        else:
                            #calculate a forward vector based on our location relative to horizontal center of the box
                            
                            p = agentList[j].history[k]
                            f = agentList[j].history[k+1]
                            mList = meshClosePt(p)
                            u = norms[mList[1]]                             
                            u = forceOrtho(u)
                            u = rs.VectorAdd(u, agentList[j].history[k])
                            targ = [p,f,u]
                            tempComp = rs.CopyObject(mComp)
                            tempComp = rs.ScaleObject(tempComp,[0,0,0],[speed,speed,speed])
                            rs.OrientObject(tempComp, ref, targ)
                

