from .FSMObject import FSMData, FSMNode, FSMTransition
class FSMConverter:
    def __init__(self):
        self.machine = FSMData()



    def toFSMObject(self, validJSON):
        #obtain information from json file
        nodes = validJSON.getStates()
        edges = validJSON.getTransitions()
        acceptingStates = validJSON.getAcceptingStates() #stores id of acceptances
        initState = validJSON.getInitialState() #stores only id 
        

        #store nodes in the dictionary, 
        for state in nodes:
            stateId = state['id']

            newNode = FSMNode(idValue = stateId)
            self.machine.addState(newNode)

        for transition in edges:
            fromState = transition['from']
            toState = transition['to']
            label = transition['label']
            newTransition = FSMTransition(label=label,fromState=fromState,toState=toState)
            newTransition.typeDummy = False
            if fromState == toState:
                self.machine.addSelfTransition(newTransition)
            else:
                self.machine.addTransition(newTransition)
            self.machine.states[fromState].addTransition(newTransition)

        currFSM = self.machine

        
        initNode = [node for node in currFSM.states.values() if node.id == initState]
        
        initNode[0].setAsInitial()
       
        currFSM.setInitialState(initNode[0])

        
        acceptingNodes = [node for node in currFSM.states.values() if node.id in acceptingStates]
        currFSM.acceptingStates.extend(acceptingNodes)

        [node.setAsAccepting() for node in acceptingNodes]

        return currFSM
    
