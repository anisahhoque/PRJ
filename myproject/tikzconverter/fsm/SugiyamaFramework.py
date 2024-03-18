from .FSMObject import FSMTransition,FSMDummyNode,FSMNode
import os
import copy
import math
import subprocess

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
        
        for i in self.feedbackSet:
            self.edgeReversal(i)

        storeLong = self.identifyLongEdges()
        
        self.insertDummyVertices(storeLong) 

        layers = {}
        for node_id, node in self.fsm.states.items():

            layer_value = node.layerValue
            if layer_value not in layers:
                layers[layer_value] = []

            
            layers[layer_value].append(node_id)

            self.assignXCoords(nodeID=node_id,layer=layer_value)

            
        return layers
    

    def dummyArrangement(self):
        storeLong = self.identifyLongEdges()
        
        self.insertDummyVertices(storeLong) 

        for i in self.fsm.dummyNodes.values():
            #self.assignDummyXCoords(i)
            pass

    
    def assignDummyYCoords(self,dummyNode):
        pass
        dummyNode.setYCoord(dummyNode.layerValue)
        
    def assignDummyXCoords(self):
        pass
    
    def assignXCoords(self,nodeID,layer):
        self.fsm.states[nodeID].setXCoord(layer*2)
        
    def assignYCoords(self,layers):
        for layers in layers.values():

            verticeCount = len(layers)
            step = 10/ (verticeCount + 1)
            yCoord = round(step,1)

            for vertex in layers:
                self.fsm.states[vertex].setYCoord(yCoord)
                yCoord += step


    def vertexArrangement(self,layers):
        
        self.assignYCoords(layers) #assign default values
        
        #for layer in list(layers.values()):
        #    self.repulse(layer,2)
        #for i in range(23): #special iteration number
        #    for layer in list(layers.values()):
        #        for vertex in layer:
        #            #if type(self.fsm.states[vertex]) is (FSMNode):
        #                if self.fsm.states[vertex].layerValue == 0:
        #                    neighbours = self.getNeighboursInNextLayer(vertex, layers)
        #                elif self.fsm.states[vertex].layerValue == max(list(layers.keys())):
        #                    neighbours = self.getNeighboursInPreviousLayer(vertex, layers)
        #                else:
        #                    neighbours = self.getNeighboursInPreviousLayer(vertex, layers)
        #                    neighbours2 = self.getNeighboursInNextLayer(vertex, layers)
        #                    neighbours.extend(neighbours2)
#
        #                calculateBary = self.calculateBary(neighbours)
#
        #                if calculateBary == 0:
        #                    pass
        #                else:
        #                    self.setVertexPos(vertex, calculateBary)
        #        
        #        self.repulse(layer,1)

        

        #self.dummyArrangement()

        

    def compile(self,tikzCode):
        with open('temp.tex', 'w') as f:
            f.write(tikzCode)

        subprocess.run(['pdflatex', 'temp.tex'])

        
        subprocess.run(['rm', 'temp.tex', 'temp.aux', 'temp.log', 'temp.pdf'])
        


    def repulse(self,layer, separate):
        new = []
        for i in layer:
            new.append(self.fsm.states[i])
        layer = new
        n = len(layer)
        if n <= 1:
            return layer

        layer.sort(key=lambda v: v.y)


        displacements = [0] * n


        for i in range(1, n):
            prev_vertex = layer[i - 1]
            curr_vertex = layer[i]
            width = 2
            overlap = prev_vertex.y + width/ 2 + width / 2 - curr_vertex.y + separate
            if overlap > 0:
                displacement = overlap / 2
                displacements[i - 1] -= displacement
                displacements[i] += displacement
        for i in range(n):
            layer[i].y += displacements[i]

        return layer






    def calculateBary(self, neighbours):
        if len(neighbours) == 0:
            return 0
        total = 0
        for i in neighbours:
            if type(self.fsm.states[i]) is (FSMNode):
                total += self.fsm.states[i].y
                
        position = total/len(neighbours)
        return(position)
    
    def setVertexPos(self, nodeID, yPos):
        self.fsm.states[nodeID].setYCoord(yPos)



    def generate_tikz_code(self):
        tikz_code = []
        nodeLabels = [x.strip('#') for x in self.fsm.states.keys()]
        # Add TikZ setup commands
        
        tikz_code.append(r"\documentclass{standalone}")
        tikz_code.append(r"\usepackage{tikz}")
        tikz_code.append(r"\usetikzlibrary{automata}")  # Add automata library
        tikz_code.append(r"\begin{document}")
        #tikz_code.append(r"\begin{tikzpicture}[->,>=stealth,auto,node distance=2.5cm,semithick]")
        tikz_code.append(r"\begin{tikzpicture}[->,>=stealth,auto,node distance=2.5cm,semithick,every state/.style={minimum width=1cm, minimum height=1cm, text width=0.75cm,align=center}]")

        

        # Generate nodes
        for node_id, node in self.fsm.states.items():
            x = node.x
            y = node.y
            label = self.fsm.states[node_id].name
            if node_id == self.fsm.initialState.id and node in self.fsm.acceptingStates:
                node_id = node_id.lstrip('#')
                tikz_code.append(f"\\node[state, initial, accepting] ({node_id}) at ({x},{y}) {{{node_id}}};")
            if node_id == self.fsm.initialState.id:
                node_id = node_id.lstrip('#')
                tikz_code.append(f"\\node[state, initial] ({node_id}) at ({x},{y}) {{{node_id}}};")
            elif node in self.fsm.acceptingStates:
                node_id = node_id.lstrip('#')
                tikz_code.append(f"\\node[state, accepting] ({node_id}) at ({x},{y}) {{{node_id}}};")
            else:
                node_id = node_id.lstrip('#')
                tikz_code.append(f"\\node[state] ({node_id}) at ({x},{y}) {{{node_id}}};")

        # Generate edges
        for transition in self.fsm.transitions:
            transitionLabel = transition.label
            from_node = transition.fromState
            to_node = transition.toState 
            fromNode = self.fsm.states[from_node]
            toNode = self.fsm.states[to_node]

            fromN = transition.fromState.lstrip('#')
            toN= transition.toState.lstrip('#')
            fromLabel = fromNode.name
            toLabel = toNode.name
            if abs(toNode.layerValue - fromNode.layerValue) > 1:
                if fromNode.layerValue > toNode.layerValue:
                    tikz_code.append(f"\\path ({fromN})  edge[bend right] node {{{transitionLabel}}} ({toN});")
                if fromNode.layerValue < toNode.layerValue:
                    tikz_code.append(f"\\path ({fromN})  edge[bend left] node {{{transitionLabel}}} ({toN});")
            else:
                tikz_code.append(f"\\path ({fromN}) edge node {{}} ({toN});")


            #if abs(toNode.layerValue - fromNode.layerValue) > 1:
            #    if fromNode.layerValue > toNode.layerValue:
            #        tikz_code.append(f"\\draw ({fromLabel}) .. controls +(right:1cm) and +(left:1cm) .. ({toLabel}) node[midway, sloped, above] {{{transitionLabel}}};")
            #    elif fromNode.layerValue < toNode.layerValue:
            #        tikz_code.append(f"\\draw ({fromLabel}) .. controls +(left:1cm) and +(right:1cm) .. ({toLabel}) node[midway, sloped, below] {{{transitionLabel}}};")
            #else:
            #    tikz_code.append(f"\\draw ({fromLabel}) -- ({toLabel}) node[midway, above] {{{transitionLabel}}};")

            #tikz_code.append(f"\\path ({fromN}) edge node {{}} ({toN});")



        for transition in self.fsm.selfTransitions:
            from_node = transition.fromState.lstrip('#')
            to_node = transition.toState.lstrip('#')
            if from_node == to_node:  # Self-transition
                tikz_code.append(f"\\draw[->, loop above] ({from_node}) to ({to_node});")
            else:
                tikz_code.append(f"\\draw[->] ({from_node}) -- ({to_node});")

       
        tikz_code.append(r"\end{tikzpicture}")
        tikz_code.append(r"\end{document}")

        return '\n'.join(tikz_code)






    #doesnt care what kind of node

    def getNeighboursInPreviousLayer3(self,nodeID,layers):
        previousLayer = self.fsm.states[nodeID].layerValue - 1
        potentialNeighbours = layers[previousLayer]
        neighbours = [n for n in potentialNeighbours if any(x.toState == nodeID for x in self.fsm.states[n].transitions)]
        return neighbours

    def getNeighboursInNextLayer3(self,nodeID,layers):
        nextLayer = self.fsm.states[nodeID].layerValue + 1
        potentialNeighbours = layers[nextLayer]
        neighbours = [n for n in potentialNeighbours if any(x.toState == nodeID for x in self.fsm.states[n].transitions)]
        return neighbours
    
    #checks for fsm nodes too
    def getNeighboursInPreviousLayer(self, nodeID, layers):
        previousLayer = self.fsm.states[nodeID].layerValue - 1
        potentialNeighbours = layers[previousLayer]
        neighbours = [n for n in potentialNeighbours if type(self.fsm.states[n]) is FSMNode and any(x.toState == nodeID for x in self.fsm.states[n].transitions)]
        return neighbours
    def getNeighboursInNextLayer(self, nodeID, layers):
        previousLayer = self.fsm.states[nodeID].layerValue + 1
        potentialNeighbours = layers[previousLayer]
        neighbours = [n for n in potentialNeighbours if type(self.fsm.states[n]) is FSMNode and any(x.toState == nodeID for x in self.fsm.states[n].transitions)]
        return neighbours
    
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
        storeSort.remove(source)
        for i in storeSort:
            pred = self.findPredeccessors(i)
            predLayer = [layers[p] for p in pred]
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
                if abs(transLayerVal - currLayerVal) > 1 :
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


            dummiesForEdge = [self.fsm.states[source]] #list of nodes ------>  0--->0---->0---->0

            
            if sourceLayer < endLayer:
                
                for dummyLayers in range(sourceLayer + 1, endLayer):
                    counter += 1
                    newDummyID = dummyID + str(counter)
                    newDummy = FSMDummyNode(idValue=newDummyID, layerValue=dummyLayers)
                    self.fsm.dummyNodes[newDummyID] = newDummy
                    self.fsm.states[newDummyID] = newDummy
                    dummiesForEdge.append(newDummy)

                dummiesForEdge.append(self.fsm.states[end])
                self.fsm.longEdgeMap[edge] = dummiesForEdge
                transitions = []
                for i in range(len(dummiesForEdge) - 1):
                    fromNode = dummiesForEdge[i].id
                    toNode = dummiesForEdge[i + 1].id
                    transition = FSMTransition("",fromNode, toNode)
                    self.fsm.states[fromNode].addTransition(transition)
                    transitions.append(transition)
                self.fsm.transitions.extend(transitions)

            
            elif endLayer < sourceLayer:
                print("ghello")
                print(f"source{sourceLayer}")
                print(f"end{endLayer}")
                for dummyLayers in range(sourceLayer, endLayer+1,-1):
                    print("meow")
                    print(endLayer)
                    print(sourceLayer-1)
                    counter += 1
                    newDummyID = dummyID + str(counter)
                    print(f"DYMMYVALEUE{dummyLayers}")
                    newDummy = FSMDummyNode(idValue=newDummyID, layerValue=dummyLayers-1)
                    self.fsm.dummyNodes[newDummyID] = newDummy

                    self.fsm.states[newDummyID] = newDummy

                    dummiesForEdge.append(newDummy)
 

                dummiesForEdge.append(self.fsm.states[end])
                self.fsm.longEdgeMap[edge] = dummiesForEdge

                transitions = []
                for i in range(len(dummiesForEdge) - 1):
                    fromNode = dummiesForEdge[i].id
                    toNode = dummiesForEdge[i+1].id
                    transition = FSMTransition("",fromNode, toNode)
                    self.fsm.states[fromNode].addTransition(transition)
                    transitions.append(transition)
                self.fsm.transitions.extend(transitions)               


            
                
            










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
        
