import rhinoscriptsyntax as rs
import math
import random

#import our mesh component
mComp = rs.GetObject("select mesh component", 32)
#import our negative points in our script
negPts = rs.GetObjects("select negative points", 1)
posPts = rs.GetObjects("select positive points", 1)
#rhino has imported guid's and we need to conver them to xyz locations
negLocs = []
for i in range(len(negPts)):
    #get the vector location for the pt
    loc = rs.PointCoordinates(negPts[i])
    negLocs.append(loc)

posLocs = []
for i in range(len(posPts)):
    #get the vector location for the pt
    loc = rs.PointCoordinates(posPts[i])
    posLocs.append(loc)

#global variables
gens = 10
dimx = 10
dimy = 10
dimz = 10
agentList = []
origin = [0,0,0]
forward = [0,1,0]
up = [0,0,1]
ref = [origin,forward,up]
#a class a collection of variables and functions that can be repeated
#unlike a function no parenthesis
class agent:
    #constructor function is instructions for creating the copy of the class
    # __init__ is a specific name for constructor functions
    #self will get filled automatically
    def __init__(self, x, y):
        self.pos = [x,y,0]
        self.history = []
        self.history.append(self.pos)
        self.switch = True
    
    def update(self):        
        #setup an empty acceleration function
        acc = [0,0,0]
        #call our behavior functions
        mag = self.magnet()
        
        #add behaviors to acc
        acc = rs.VectorAdd(acc,mag)
        acc = self.forceOrtho(acc)
        
        #is add acc to self.pos
        self.pos = rs.VectorAdd(self.pos,acc)
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
    def forceOrtho(self, inVec):
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
            
    def render(self):
        if self.switch == True:
            rs.AddPoint(self.pos)

#this loops create the agents at their original positions
for i in range(dimx):
    for j in range(dimy):
        r = random.random()
        if r < .2:
            #when call the name of the class you are calling the constructor function in the class
            #when passing values into the constructor, you don't put something in for the "self"
            a = agent(i,j)
            #we can then call function inside that class
            a.render()
            #put our agent in the agentList
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
                            rs.OrientObject(tempComp,ref,targ)
                        else:
                            #calculate a forward vector based on our location relative to horizontal center of the box
                            center = [dimx/2,dimy/2, agentList[j].history[k][2]]
                            if rs.Distance(center,agentList[j].history[k]) > 0:
                                f = rs.VectorCreate(center,agentList[j].history[k])                                
                                f = agentList[j].forceOrtho(f)
                                f = rs.VectorAdd(f, agentList[j].history[k])
                                p = agentList[j].history[k]
                                u = rs.VectorAdd(p,up)
                                targ = [p,f,u]
                                tempComp = rs.CopyObject(mComp)
                                rs.OrientObject(tempComp, ref, targ)
                

myList = []
myList.append(7)
myList.append(2)
myList.append(10)
myList.append(12)
print(myList)
#lists start at 0
#[0,1,2,3]
#[7,2,10,12]
num = myList[1] + myList[3]
print(num)