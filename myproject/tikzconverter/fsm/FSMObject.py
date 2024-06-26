class FSMData:
    def __init__(self):
        self.transitions = [] 
        self.states = {} #lookup with id
        self.initialState = None
        self.acceptingStates = [] #stores objects
        self.selfTransitions = []
        self.longEdgeMap = {}
        self.dummyNodes = {}

    def addState(self, state):
        self.states[state.id] = state

    def setInitialState(self, state):
        self.initialState = state

    def addAcceptingState(self, state):
        self.acceptingStates.append(state)

    def addTransition(self,transition):
        self.transitions.append(transition)

    def addSelfTransition(self,transition):
        self.selfTransitions.append(transition)


    def removeTransition(self,transition):
        self.transitions.remove(transition)

    def removeSelfTransition(self,transition):
        self.selfTransitions.remove(transition)

    def addDummyNode(self,dummy):
        self.dummyNodes[dummy.id] = dummy

    def getInitial(self):
        return self.initialState
    
    def getStates(self):
        return self.states
    
    def getAcceptingStates(self):
        return self.acceptingStates
    
    def getTransitions(self):
        return self.transitions
    
    def getSelfTransitions(self):
        return self.selfTransitions
    

class FSMNode:
    def __init__(self,idValue):
        self.id = idValue
        self.transitions = []
        self.selfTransitions = []
        self.hasSelfTransition = False
        self.isInital = False
        self.isAccepting = False
        self.layerValue = None
        self.x = 0
        self.y = 0
        self.vertexPos = None

    def addTransition(self, transition):
        if transition.fromState == transition.toState:
            if self.hasSelfTransition == False:
                self.hasSelfTransition = True
            self.selfTransitions.append(transition)
        else:
            self.transitions.append(transition)

    def removeTransition(self,transition):
        self.transitions.remove(transition)

    def setAsInitial(self):
        self.isInitial = True

    def setAsAccepting(self):
        self.isAccepting = True

    def setXCoord(self,x):
        self.x = x
    
    def setYCoord(self,y):
        self.y = y
    
    def getXCoord(self):
        return self.x
    
    def getYCoord(self):
        return self.y

class FSMTransition:
    def __init__(self,label,fromState,toState):
        self.label = label
        self.fromState = fromState
        self.toState = toState
        self.typeDummy = False

    def getLabel(self):
        return self.label
    def getFrom(self):
        return self.fromState
    def getTo(self):
        return self.toState
    def getIsDummy(self):
        return self.typeDummy
    
class FSMDummyNode(FSMNode):
    def __init__(self, idValue, layerValue):
        super().__init__(idValue)
        self.layerValue = layerValue




