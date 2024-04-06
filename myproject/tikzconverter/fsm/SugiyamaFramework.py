from .FSMObject import FSMTransition,FSMDummyNode
import os
import subprocess
from django.conf import settings



class SugiyamaFramework:
    def __init__(self,FSMData):
        self.fsm = FSMData
        self.feedbackSet = []
        self.hyperparameters = {'bend': 15,'width':4,'height':5}
        self.tikzCode = None


    def dfs(self, node, visited, path, cycles):
        visited.add(node.id)
        path.append(node.id)

        for transition in node.transitions:
            neighbourID = transition.toState
            if neighbourID in path:
                cycleStart = path.index(neighbourID)
                cycle = path[cycleStart:]
                cycles.append(cycle)
                self.feedbackSet.append(transition)
                self.edgeReversal(transition)
                
            elif neighbourID not in visited:
                neighbourNode = self.fsm.states[neighbourID]
                self.dfs(neighbourNode, visited, path, cycles)

        path.pop()

    def detectCycles(self):
        visited = set()
        cycles = []
        for stateID, state in self.fsm.states.items():
            if stateID not in visited:
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
        toNode.transitions.append(transition)


    def layerAssignment4(self):
        self.assignLayers()
    
        for i in self.feedbackSet:
            self.edgeReversal(i)

        storeLong = self.identifyLongEdges()
        self.insertDummyVertices(storeLong) 

        layers = {}
        for nodeID, node in self.fsm.states.items():
            layerValue = node.layerValue
            if layerValue not in layers:
                layers[layerValue] = []

            layers[layerValue].append(nodeID)
            self.assignXCoords(nodeID=nodeID,layer=layerValue)
        barySorted = self.bary(layers)

        return barySorted
    
    def bary(self, layers):
        barycenters = {}
        for layer, vertices in layers.items():
            if layer == 0:
                continue
            else:
                previouslayer = layers[layer-1]
                for vertex in vertices:
                    neighbours = self.getNeighboursInPreviousLayer3(vertex, layers)
                    if neighbours:  # Check if the neighbor list is not empty
                        neighbourPos = [previouslayer.index(neighbour) for neighbour in neighbours]
                        barycenter = sum(neighbourPos) / len(neighbours)
                    barycenters[vertex] = barycenter
        
        sortedLayers = {}
        for layer, vertices in layers.items():
            sortedVertices = sorted(vertices, key=lambda vertex: barycenters.get(vertex, 0))
            sortedLayers[layer] = sortedVertices


        return sortedLayers


 

    

    def dummyArrangement(self):
        storeLong = self.identifyLongEdges()
        
        self.insertDummyVertices(storeLong) 

        layers = {}
        for nodeID, node in self.fsm.dummyNodes.items():

            layerValue = node.layerValue
            if layerValue not in layers:
                layers[layerValue] = []

            
            layers[layerValue].append(nodeID)

            self.assignXCoords(nodeID=nodeID,layer=layerValue)
            


    def assignXCoords(self,nodeID,layer):
        self.fsm.states[nodeID].setXCoord(layer*self.hyperparameters['width'])
        
    def assignYCoords(self,layers):
        for layers in layers.values():

            verticeCount = len(layers)
            step = self.hyperparameters['height'] / (verticeCount + 1)
            yCoord = round(step,1)

            for vertex in layers:
                self.fsm.states[vertex].setYCoord(yCoord)
                yCoord += step


    def vertexArrangement(self, sortedLayers):
        vertexSeperation = self.hyperparameters['height']

        # Assign priorities to vertices based on their connectivity and dummy status
        priorities = {}
        for layer, nodes in sortedLayers.items():
            for node in nodes:
                priority = 0
                if node in self.fsm.dummyNodes:
                    priority += 1000  # Give highest priority to dummy vertices
                for transition in self.fsm.transitions:
                    if transition.fromState == node:
                        if layer > 0 and transition.toState in sortedLayers[layer - 1]:
                            priority += 1  # Increase priority based on connections to the previous layer
                priorities[node] = priority

        # Assign y-coordinates to vertices based on their priorities
        for layer, nodes in sortedLayers.items():
            # Sort nodes based on their priorities (higher priority first)
            sortedNodes = sorted(nodes, key=lambda x: priorities[x], reverse=True)

            # Assign y-coordinates to nodes
            yCoord = 0
            for node in sortedNodes:
                self.fsm.states[node].y = yCoord
                yCoord += vertexSeperation

            # Adjust y-coordinates of lower priority nodes if needed
            for i in range(len(sortedNodes)):
                node = sortedNodes[i]
                if node not in self.fsm.dummyNodes:
                    continue
                dummyY = self.fsm.states[node].y
                for transition in self.fsm.transitions:
                    if transition.fromState == node:
                        neighbor = transition.toState
                        if layer < len(sortedLayers) - 1 and neighbor in sortedLayers[layer + 1]:
                            neighbourY = self.fsm.states[neighbor].y
                            if abs(dummyY - neighbourY) > vertexSeperation:
                                # Adjust y-coordinate of the lower priority neighbor
                                self.fsm.states[neighbor].y = dummyY

        # Find the initial node
        initialNode = self.fsm.initialState

        # Calculate the offset based on the initial node's y-coordinate
        offset = self.fsm.states[initialNode.id].y

        # Adjust the y-coordinates of all vertices by subtracting the offset
        for state in self.fsm.states.values():
            state.y -= offset

  
        






        
    def compileTikz(self, tikzCode, outputFileName='output.pdf'):
        mediaFolder = settings.MEDIA_ROOT
        outputFilePath = os.path.join(mediaFolder, outputFileName)


        if os.path.exists(outputFilePath):
            os.remove(outputFilePath)


        tempTexPath = os.path.join(mediaFolder, 'temp.tex')
        with open(tempTexPath, 'w') as f:
            f.write(tikzCode)
        
        try:
            subprocess.run(['pdflatex', '-interaction=nonstopmode', tempTexPath], check=True, cwd=mediaFolder)
        except subprocess.CalledProcessError as e:
            print(f"Error compiling TikZ code: {e}")
            return
        tempPDFPath = os.path.join(mediaFolder, 'temp.pdf')
        if os.path.exists(tempPDFPath):
            subprocess.run(['mv', tempPDFPath, outputFilePath], check=True)
            print(f"TikZ code compiled to {outputFileName}")
        else:
            print("Error: temp.pdf file not generated.")










    def generateTikzCode(self):
        new = Latex
        bend = self.hyperparameters['bend']
        tikzCode = []
        
        
        
        tikzCode.append(r"\documentclass{standalone}")
        tikzCode.append(r"\usepackage{tikz}")
        tikzCode.append(r"\usetikzlibrary{automata,positioning}")  
        tikzCode.append(r"\begin{document}")
        tikzCode.append(r"\begin{tikzpicture}[->,>=stealth,auto,node distance=2.5cm,semithick,every state/.style={minimum width=1cm, minimum height=1cm, text width=0.75cm,align=center}]")


  
        for nodeID, node in self.fsm.states.items():
            x = node.x
            y = node.y
            if type(self.fsm.states[nodeID]) is FSMDummyNode:
                continue
            
            nodeLabel = nodeID.lstrip('#')
            if nodeID == self.fsm.initialState.id and node in self.fsm.acceptingStates:
                tikzCode.append(f"\\node[state, initial, accepting] ({nodeLabel}) at ({x},{y}) {{{nodeLabel}}};")
            elif nodeID == self.fsm.initialState.id:
                tikzCode.append(f"\\node[state, initial] ({nodeLabel}) at ({x},{y}) {{{nodeLabel}}};")
            elif node in self.fsm.acceptingStates:
                tikzCode.append(f"\\node[state, accepting] ({nodeLabel}) at ({x},{y}) {{{nodeLabel}}};")
            else:
                
                tikzCode.append(f"\\node[state] ({nodeLabel}) at ({x},{y}) {{{nodeLabel}}};")

        for longEdge, dummyNodes in self.fsm.longEdgeMap.items():
            sourceNode = self.fsm.states[longEdge.fromState]
            endNode = self.fsm.states[longEdge.toState]
            transitionLabel = longEdge.label
            sourceLabel = sourceNode.id.lstrip('#')
            endLabel = endNode.id.lstrip('#')
            if abs(sourceNode.layerValue - endNode.layerValue) == 1:
                if sourceNode.layerValue < endNode.layerValue:
                    tikzCode.append(f"\\draw[->, rounded corners={bend}pt] ({sourceLabel}) to[bend left=30] node[midway, sloped, above] {{{transitionLabel}}} ({endLabel});")
                else:
                    tikzCode.append(f"\\draw[->, rounded corners={bend}pt] ({sourceLabel}) to[bend right=30] node[midway, sloped, above] {{{transitionLabel}}} ({endLabel});")
            else:

                if type(sourceNode) is FSMDummyNode:
                    edgePath = f"({sourceNode.x},{sourceNode.y})"
                else:
                    edgePath = f"({sourceLabel})"

                for dummyNode in dummyNodes[1:-1]: 
                    edgePath += f" -- ({dummyNode.x},{dummyNode.y})"

                if type(endNode) is FSMDummyNode:
                    edgePath += f" -- ({endNode.x},{endNode.y})"
                else:
                    edgePath += f" -- ({endLabel})"

                
                tikzCode.append(f"\\draw[->, rounded corners={bend}pt] {edgePath} node[midway, sloped, above] {{{transitionLabel}}};")

      
        for transition in self.fsm.transitions:
            label = transition.label
            if transition.typeDummy == True:
                continue
            elif transition.typeDummy == False:
                fromNode = transition.fromState
                toNode = transition.toState 


                fromN = transition.fromState.lstrip('#')
                toN= transition.toState.lstrip('#')

                tikzCode.append(f"\\path ({fromN}) edge node[midway, sloped, above] {{{label}}} ({toN});")
        
        for transition in self.fsm.selfTransitions:
            fromNode = transition.fromState.lstrip('#')
            toNode = transition.toState.lstrip('#')
            label = transition.label[:3]
            if fromNode == toNode:  # Self-transition
                tikzCode.append(f"\\draw[->, loop above] ({fromNode}) to node[sloped, above] {{{label}}} ({toNode});")
            else:
                tikzCode.append(f"\\draw[->] ({fromNode}) -- node[midway, sloped, above] {{{label}}} ({toNode});")

        tikzCode.append(r"\end{tikzpicture}")
        tikzCode.append(r"\end{document}")

        return '\n'.join(tikzCode)






    #checks for all node types
    def getNeighboursInPreviousLayer3(self,nodeID,layers):
        previousLayer = self.fsm.states[nodeID].layerValue - 1
        potentialNeighbours = layers[previousLayer]
        neighbours = [n for n in potentialNeighbours if any(x.toState == nodeID for x in self.fsm.states[n].transitions)]
        return neighbours



    def dfsForSort(self, node, visited, stack):
        visited.add(node)
        for transition in node.transitions:
            neighbourID = transition.toState
            neighbourNode = self.fsm.states[neighbourID]
            if neighbourNode not in visited:
                self.dfsForSort(neighbourNode, visited, stack)
        stack.append(node)

    def topologicalSort(self):
        visited = set()
        stack = []
        for stateID, state in self.fsm.states.items():
            if state not in visited:
                self.dfsForSort(state, visited, stack)
        sortedNodes = [node.id for node in reversed(stack)]
        return sortedNodes
    


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
                    transition.typeDummy = True
                    self.fsm.states[fromNode].addTransition(transition)
                    transitions.append(transition)
                self.fsm.transitions.extend(transitions)

            
            elif endLayer < sourceLayer:

                for dummyLayers in range(sourceLayer, endLayer+1,-1):
                    counter += 1
                    newDummyID = dummyID + str(counter)
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
                    transition.typeDummy = True
                    self.fsm.states[fromNode].addTransition(transition)
                    transitions.append(transition)
                self.fsm.transitions.extend(transitions)               



    def findPredeccessors(self,nodeID):
        predeccessors = []
        for i in self.fsm.transitions:
            if i.toState == nodeID:
                predeccessors.append(i.fromState)
        return(predeccessors)
                




