from FSMObject import FSMTransition,FSMDummyNode

import copy
class SugiyamaFramework:
    def __init__(self,FSMData):
        self.fsm = FSMData
        self.feedbackSet = []




    def dfs(self, node, visited, path, cycles):
        visited.add(node.id)
        path.append(node.id)

        for transition in node.transitions:
            neighbor_id = transition.toState
            if neighbor_id in path:
                cycle_start_index = path.index(neighbor_id)
                cycle = path[cycle_start_index:]
                cycles.append(cycle)
                self.feedbackSet.append(transition)
                self.edgeReversal(transition)
            elif neighbor_id not in visited:
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
        fromNode = self.fsm.states[fromState]
        toNode = self.fsm.states[toState]

        #update nodes
        fromNode.transitions.remove(transition)
        #reversedTransition = FSMTransition(label=transition.label, fromState=toState, toState=fromState)
        toNode.transitions.append(transition)



    def layerAssignment(self):
        self.assignLayers()
        
        storeLong = self.identifyLongEdges()
        self.insertDummyVertices(storeLong)
        #for i in list(self.fsm.states.keys()):
        #    print("NODE")
        #    print(i)
        #    print("layer")
        #    print(self.fsm.states[i].layerValue)
        #    print("trans")
        #    for j in self.fsm.states[i].transitions:
        #        print(j.toState)
        #    print("----")
        #print(self.convert_to_tikz(layers=sortedNodes))

        layers = {}
        for node_id, node in self.fsm.states.items():
            layer_value = node.layerValue
            if layer_value not in layers:
                layers[layer_value] = []

            
            layers[layer_value].append(node_id)
            self.assignXCoords(nodeID=node_id,layer=layer_value)
        return layers
    
    def assignXCoords(self,nodeID,layer):
        self.fsm.states[nodeID].x = layer
        
    def assignYCoords(self,layers):
        for layers in layers.values():

            verticeCount = len(layers)
            step = 1 / (verticeCount + 1)
            yCoord = step 

            for vertex in layers:
                self.fsm.states[vertex].y= yCoord
                yCoord += step
    def vertexArrangement(self,layers):
        self.assignYCoords(layers) #assign default values

    
    def getNeighboursInPreviousLayer(self,nodeID,layers):
        previousLayer = self.fsm.states[nodeID]
    
    def dfsForSort(self, node, visited, stack):
        visited.add(node)
        for transition in node.transitions:
            neighbor_id = transition.toState
            neighbor_node = self.fsm.states[neighbor_id]
            if neighbor_node not in visited:
                self.dfsForSort(neighbor_node, visited, stack)
        stack.append(node)

    def topologicalSort(self):
        visited = set()
        stack = []
        for state_id, state in self.fsm.states.items():
            if state not in visited:
                self.dfsForSort(state, visited, stack)
        sorted_nodes = [node.id for node in reversed(stack)]
        return sorted_nodes
    


    def assignLayers(self):
        storeSort = self.topologicalSort()
        layers = {}  # Dictionary to store layers of nodes
        source = self.fsm.initialState.id  # Set the initial state as the source node
        layers[source] = 0
        self.fsm.states[source].layerValue = 0
        #print(layers)
        storeSort.remove(source)
        for i in storeSort:
            #print("CURRENT NODE")
            #print(i)
            #print("PREDECCESSORS")
            pred = self.findPredeccessors(i)
            #print(pred)
            predLayer = [layers[p] for p in pred]
            #print(predLayer)
            maxPredLayer = max(predLayer)
            layers[i] = maxPredLayer + 1
            self.fsm.states[i].layerValue = maxPredLayer + 1

        return(layers)
    

    def identifyLongEdges(self):
        storeLongEdges = []
        nodes = list(self.fsm.states.keys())

        for i in nodes:
            
            currLayerVal = self.fsm.states[i].layerValue
            
            for j in self.fsm.states[i].transitions:
                transLayerVal = self.fsm.states[j.toState].layerValue
                if transLayerVal - currLayerVal > 1 :
                    storeLongEdges.append(j)
   
        
        return (storeLongEdges)


    def insertDummyVertices(self, longEdges):
        dummyID = "#0"
        counter = 0
        for edge in longEdges:

            self.fsm.transitions.remove(edge)

            source = edge.fromState
            end = edge.toState
            sourceLayer = self.fsm.states[source].layerValue
            endLayer = self.fsm.states[end].layerValue

            self.fsm.states[source].transitions.remove(edge)
            dummiesForEdge = [self.fsm.states[source]]
            for dummyLayers in range(sourceLayer+1,endLayer):
                counter += 1
                newDummyID = dummyID + str(counter)
                newDummy = FSMDummyNode(idValue=newDummyID,layerValue= dummyLayers)
                self.fsm.states[newDummyID] = newDummy
                dummiesForEdge.append(newDummy)

            dummiesForEdge.append(self.fsm.states[end])
            transitions = []
            for i in range(len(dummiesForEdge) - 1):
                fromNode = dummiesForEdge[i].id
                toNode = dummiesForEdge[i + 1].id
                transition = FSMTransition("",fromNode, toNode)
                self.fsm.states[fromNode].addTransition(transition)
                transitions.append(transition)
            self.fsm.transitions.extend(transitions)
            
                
            









    
   
    def convert_to_tikz(self, layers, node_size=1):
        tikz_code = "\\begin{tikzpicture}\n"
        for node_id, layer in layers.items():
            x = layer  # x-coordinate based on layer
            y = node_id  # y-coordinate based on node ID (or any other ordering)
            tikz_code += f"\\node[draw, circle, minimum size={node_size}cm] ({node_id}) at ({x},{y}) {{{node_id}}};\n"
        # Add TikZ commands to draw edges between nodes
        # Example: tikz_code += "\\draw (A) -- (B);\n"
        tikz_code += "\\end{tikzpicture}"
        return tikz_code








    def findPredeccessors(self,nodeID):
        predeccessors = []
        for i in self.fsm.transitions:
            if i.toState == nodeID:
                predeccessors.append(i.fromState)
        return(predeccessors)
                

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
        

