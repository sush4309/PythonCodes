import rhinoscriptsyntax as rs
import math
import random

#import our mesh component
mComp1 = rs.GetObjects("select mesh component for zero connect", 32)
mComp2 = rs.GetObjects("select mesh component for single connect", 32)
mComp3 = rs.GetObjects("select mesh component for double straight connect", 32)
mComp4 = rs.GetObjects("select mesh component for double L connect", 32)
mComp5 = rs.GetObjects("select mesh component for triple connect", 32)
mComp6 = rs.GetObjects("select mesh component for quad connect", 32)
mCompList = [mComp1,mComp2,mComp3,mComp4,mComp5,mComp6]

#import our starting positions
startPts = rs.GetObjects("select starting cells",1)

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
dimx = 8
dimy = 11
dimz = 10
agentList = []
origin = [0,0,0]
forward = [0,1,0]
up = [0,0,1]
ref = [origin,forward,up]

#setup initial voxel grid
grid = []
for i in range(dimx):
    row = []
    for j in range(dimy):
        col = []
        for k in range(dimz):
            col.append(0)
        row.append(col)
    grid.append(row)

dirGrid = []
for i in range(dimx):
    row = []
    for j in range(dimy):
        col = []
        for k in range(dimz):
            col.append([0,0,0])
        row.append(col)
    dirGrid.append(row)
    
    
def calculateGridConnections():
    #loop through every cell in grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            for k in range(len(grid[i][j])):
                #first check if our cell is not zero
                if grid[i][j][k] != 0:
                    #loop through x and y -1 to 1 to see if our neighbors are on and store if they are 
                    #by adding 1 to connect
                    connect = 0
                    #[[-1,0],[0,-1],[0,1],[1,0]]
                    sumVec = [0,0,0]
                    testList = [0,0,0,0]
                    listCount = 0
                    for x in range(-1,2):
                        for y in range(-1,2):
                            if abs(x) != abs(y):
                                x1 = x + i
                                y1 = y + j
                                if x1 >= 0 and x1 < dimx and y1 >= 0 and y1 < dimy :
                                    if grid[x1][y1][k] != 0:
                                        connect += 1
                                        tempVec = [x,y,0]
                                        sumVec = rs.VectorAdd(sumVec,tempVec)
                                        testList[listCount] = 1
                                listCount += 1
                    #reset grid[i][j][k] to be equal to the number of connections plus 1 (to avoid confusion with empty cells)
                    grid[i][j][k] = connect+1
                    if connect == 1:
                        dirGrid[i][j][k] = sumVec
                    if connect == 2:
                        #first check if an L
                        if sumVec[0] != 0 and sumVec[1] != 0:
                            #unitize the sumVec and rotate it 45
                            sumVec = rs.VectorUnitize(sumVec)
                            sumVec = rs.VectorRotate(sumVec,45,[0,0,1])
                            #we need to unitize after rotating to cleanup rhino float errors
                            sumVec = rs.VectorUnitize(sumVec)
                            dirGrid[i][j][k] = sumVec
                            grid[i][j][k] = 4
                        else:
                            grid[i][j][k] =  3
                            #its a straight line
                            if testList[0] != 0:
                                #its a horizontal line
                                tempVec = [1,0,0]
                                dirGrid[i][j][k] = tempVec
                            else:
                                tempVec = [0,1,0]
                                dirGrid[i][j][k] = tempVec
                    if connect == 3:
                        grid[i][j][k] = 5
                        dirGrid[i][j][k] = sumVec
                    if connect == 4:
                        grid[i][j][k] = 6

#forceOrtho works in 3D 
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
    def __init__(self, x, y):
        self.pos = [x,y,0]
        self.history = []
        self.history.append(self.pos)
        self.switch = True
        grid[x][y][0] = 1
        dirGrid[x][y][0] = [0,0,1]
    
    def update(self):        
        #setup an empty acceleration function
        acc = [0,0,0]
        #call our behavior functions
        mag = self.magnet()
        avd = self.avoid()
        coh = self.cohesion()
        
        #adjust weights for each behavior
        mag = rs.VectorScale(mag,1)
        avd = rs.VectorScale(avd,1)
        coh = rs.VectorScale(coh,1)
        grav = [0,0,.5]
        
        #add behaviors to acc        
        acc = rs.VectorAdd(acc,mag)
        acc = rs.VectorAdd(acc,avd)
        acc = rs.VectorAdd(acc,coh)
        acc = rs.VectorAdd(acc,grav)
        acc = forceOrtho(acc)
        
        #is add acc to self.pos
        self.pos = rs.VectorAdd(self.pos,acc)
        self.colCheck()
        x = int(self.pos[0])
        y = int(self.pos[1])
        z = int(self.pos[2])
        #check to make sure our agent is inside the grid space
        if x >= 0 and x < dimx and y >= 0 and y < dimy and z >= 0 and z < dimz:
            grid[x][y][z] = 1
            dirGrid[x][y][z] = [acc[0], acc[1], acc[2]]
        #add our position to history
        self.history.append(self.pos)
    
    #check if colliding
    def colCheck(self):
        for i in range(len(agentList)):
            for j in range(len(agentList[i].history)):
                dis = rs.Distance(self.pos, agentList[i].history[j])
                if dis == 0:
                    self.switch = False
    
    def avoid(self):
        #create a zero vector to add all our avoid vectors to
        sum = [0,0,0]
        #loop through every agent in the scene
        for i in range(len(agentList)):
            other = agentList[i]
            if other != self:
                for j in range(len(other.history)):
                    dis = rs.Distance(other.history[j], self.pos)
                    if dis < 1.2 and dis > 0:
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
                    if dis > 2 and dis < 4:
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
    
    
            
    def render(self):
        if self.switch == True:
            rs.AddPoint(self.pos)

#this loops create the agents from starting positions
for pt in startPts:
    loc = rs.PointCoordinates(pt)
    a = agent(int(loc[0]),int(loc[1]))
    agentList.append(a)


#the number of times we want the agent to move
for i in range(gens):
    #loop through every agent and move them
    for j in range(len(agentList)):
        #call the update and render for each agent
        if agentList[j].switch:
            agentList[j].update()
            agentList[j].render()

#once all of the agents are done moving, we need to loop through the grid and calculate each cells number of connections
calculateGridConnections()
for i in range(len(grid)):
    for j in range(len(grid[i])):
        for k in range(len(grid[i][j])):
            if grid[i][j][k] != 0:
                #want calculate our information for orienting
                pos = [i,j,k]                
                u = rs.VectorAdd(pos,up)
                f = dirGrid[i][j][k]
                if f[2] == 0:
                    f = rs.VectorAdd(pos,f)
                else:
                    center = [dimx/2,dimy/2,k]
                    if rs.Distance(center, pos) > 0:
                        f = rs.VectorCreate(pos,center)
                        f = forceOrtho(f)
                        f = rs.VectorAdd(f,pos)
                    else:
                        f = [1,0,0]
                        f = rs.VectorAdd(f,pos)
                targ = [pos,f,u]  
                for tMesh in mCompList[grid[i][j][k]-1]:
                    tempObj = rs.CopyObject(tMesh)
                    rs.OrientObject(tempObj,ref,targ)
                    rs.ObjectLayer(tempObj,"meshOutput")