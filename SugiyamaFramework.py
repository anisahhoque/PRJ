class SugiyamaFramework:
    def __init__(self,FSMData):
        self.fsm = FSMData
        self.feedbackSet = {"lrDir":None, "reverseDir":None}

    def dfs(self, node, visited, path, cycles):
        visited.add(node.id)
        path.append(node.id)

        for transition in node.transitions:
            neighbor_id = transition.toState
            if neighbor_id in visited:
                cycle_start_index = path.index(neighbor_id)
                cycle = path[cycle_start_index:]
                cycles.append(cycle)

            else:
                neighbor_node = self.fsm.states[neighbor_id]
                self.dfs(neighbor_node, visited, path, cycles)

        path.pop() 

    def detectCycles(self):
        visited = set()
        cycles = []
        for state_id, state in self.fsm.states.items():
            if state_id not in visited:
                self.dfs(state, visited, [], cycles)
        return cycles

    def edgeReversal(self, transition):
        fromState = transition.fromState
        toState = transition.toState
        transition.fromState = toState
        transition.toState = fromState

    def returnTransitionsOfCycles(self, cycles):
        #[['#0', '#1', '#2'], ['#0', '#1', '#2', '#3', '#4']]
        cycleTransitions = []
        for cycle in cycles:
            print(cycle)
            transitions = []
            for i,nodeIDfrom in enumerate(cycle):
                print(i)
                print(nodeIDfrom)
                nextI = (i + 1) % len(cycle)
                transition = self.returnTransition(nodeIDfrom,cycle[nextI])
                transitions.append(transition)
            transitions.append(self.returnTransition(cycle[-1],cycle[0]))
            cycleTransitions.append(transitions)
        
        return cycleTransitions
    


    def returnTransition(self, fromState, toState):
        for i in self.fsm.transitions:
            if i.fromState == fromState and i.toState == toState:
                return i
            

    def removeByCommonTrans(self, cycleTransitions):
        commonTransitions = []
        for i in range(len(cycleTransitions)):
            for j in range(i + 1, len(cycleTransitions)):
                cycle1Transitions = set(cycleTransitions[i])
                cycle2Transitions = set(cycleTransitions[j])
                common = cycle1Transitions.intersection(cycle2Transitions)
                commonTransitions.extend(list(common))
        return commonTransitions
    
    def removeCycles(self, commonTransitions):
        for i in commonTransitions:
            pass
        

