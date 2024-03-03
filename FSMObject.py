class FSMData:
    def __init__(self):
        self.transitions = []
        self.states = {} #lookup with id
        self.initialState = None
        self.acceptingStates = []
        self.selfTransitions = []

    def addState(self, state):
        self.states[state.id] = state

    def setInitialState(self, state):
        self.initialState = state

    def addAcceptingState(self, state):
        self.acceptingStates.append(state)

    def addTransition(self,transition):
        self.transitions.append(transition)

    def removeTransition(self,transition):
        self.transitions.remove(transition)

    def removeSelfTransitions(self,transitions):
        pass
    

class FSMNode:
    def __init__(self,idValue,name=""):
        self.id = idValue
        self.name = name
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
        #seperate the types of transitions
        if transition.fromState == transition.toState:
            if self.hasSelfTransition == False:
                self.hasSelfTransition = True
            self.selfTransitions.append(transition)
        else:
            self.transitions.append(transition)

    def setAsInitial(self):
        self.isInitial = True

    def setAsAccepting(self):
        self.isAccepting = True

class FSMDummyNode(FSMNode):
    def __init__(self, idValue, layerValue):
        super().__init__(idValue)
        self.layerValue = layerValue



class FSMTransition:
    def __init__(self,label,fromState,toState):
        self.label = label
        self.fromState = fromState
        self.toState = toState


