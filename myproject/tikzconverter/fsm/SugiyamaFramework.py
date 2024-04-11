from .FSMObject import FSMTransition,FSMDummyNode
import os
import subprocess
from django.conf import settings



class SugiyamaFramework:
    def __init__(self,FSMData):
        self.fsm = FSMData
        self.feedbackSet = []
        self.hyperparameters = {'bend': 15,'width':4,'height':5, 'orientation': 'horizontal'}
        self.tikzCode = None


    def dfs(self, node, visited, path, cycles):
        visited.add(node.id)
        path.append(node.id)

        for transition in node.transitions:
            neighbourID = transition.getTo()
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

        #update node objects
        fromNode.transitions.remove(transition)
        toNode.transitions.append(transition)


    def layerAssignment(self):
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
        

        return layers
    
    def barycenter(self, layers):
        barycenters = {}
        for layer, vertices in layers.items():
            if layer == 0:
                continue
            else:
                previouslayer = layers[layer-1]
                for vertex in vertices:
                    neighbours = self.getNeighboursInPreviousLayer(vertex, layers)
                    if neighbours:  
                        neighbourPos = [previouslayer.index(neighbour) for neighbour in neighbours]
                        barycenter = sum(neighbourPos) / len(neighbours)
                    barycenters[vertex] = barycenter
            layers[layer].reverse()
        
        sortedLayers = {}
        for layer, vertices in layers.items():
            sortedVertices = sorted(vertices, key=lambda vertex: barycenters.get(vertex, 0))
            sortedLayers[layer] = sortedVertices
        return sortedLayers


 


            


    def assignXCoords(self,nodeID,layer):
        if self.hyperparameters['orientation'] == 'vertical':
            self.fsm.states[nodeID].setXCoord(layer*self.hyperparameters['height'])
        else:
            self.fsm.states[nodeID].setXCoord(layer*self.hyperparameters['width'])

    def vertexArrangement(self, layers):
        sortedLayers = self.barycenter(layers)
        return sortedLayers
    def coordinateAssignment(self,sortedLayers):
        if self.hyperparameters['orientation'] == 'vertical':
            vertexSeperation = self.hyperparameters['width']
        else:
            vertexSeperation = self.hyperparameters['height']

        priorities = {}
        for layer, nodes in sortedLayers.items():
            for node in nodes:
                priority = 0
                if node in self.fsm.dummyNodes:
                    priority += 1000  
                
                if layer > 0:
                    neighbourCount = len(self.getNeighboursInPreviousLayer(node,sortedLayers))
                    priority += neighbourCount


                priorities[node] = priority


        maxHeight = max(len(x) for x in sortedLayers.values())
        yCoord = ((maxHeight -1)*vertexSeperation/2)*-1
        for layer, nodes in sortedLayers.items():
            sortedNodes = sorted(nodes, key=lambda x: priorities[x], reverse=True)
            lenAdjust = len(sortedNodes)
            yCoord = maxHeight*vertexSeperation/2
            yCoord = yCoord - (vertexSeperation*((lenAdjust//2)))
            
            for node in sortedNodes:
               
                self.fsm.states[node].y = yCoord
                yCoord += vertexSeperation 
                

        
        barycenters = {}
        for layer, vertices in sortedLayers.items():
            if layer == 0:
                for i in vertices:
                    barycenters[i] = maxHeight*vertexSeperation/2
            else:
                for vertex in vertices:
                    neighbours = self.getNeighboursInPreviousLayer(vertex, sortedLayers)
                    if neighbours:
                        neighbourPos = [self.fsm.states[neighbour].getYCoord() for neighbour in neighbours]
                        barycenter = sum(neighbourPos) / len(neighbours)
                        barycenters[vertex] = barycenter
  

        
        for layer, nodes in sortedLayers.items():
            sortedNodes = sorted(nodes, key=lambda x: (barycenters[x], priorities[x]), reverse=True)
            print(sortedNodes)
   
            assignedYCoords = set()
            for node in sortedNodes:
                yCoord = barycenters[node]
                
                
                while yCoord in assignedYCoords:
                    yCoord += vertexSeperation
                
                self.fsm.states[node].y = yCoord
                assignedYCoords.add(yCoord)



        if self.hyperparameters['orientation'] == 'vertical':
            
            for state in self.fsm.states.values():
                state.x, state.y = state.y, state.x*-1


    def coordinateAssignment1(self,sortedLayers):
        if self.hyperparameters['orientation'] == 'vertical':
            vertexSeperation = self.hyperparameters['width']
        else:
            vertexSeperation = self.hyperparameters['height']

        priorities = {}
        for layer, nodes in sortedLayers.items():
            for node in nodes:
                priority = 0
                if node in self.fsm.dummyNodes:
                    priority += 1000  
                for transition in self.fsm.transitions:
                    if transition.fromState == node:
                        if layer > 0 and transition.toState in sortedLayers[layer - 1]:
                            priority += 1  
                priorities[node] = priority

 
        for layer, nodes in sortedLayers.items():

            sortedNodes = sorted(nodes, key=lambda x: priorities[x], reverse=True)

  
            yCoord = 0
            for node in sortedNodes:
                self.fsm.states[node].y = yCoord
                yCoord += vertexSeperation


            for i in range(len(sortedNodes)):
                node = sortedNodes[i]
                if node not in self.fsm.dummyNodes:
                    continue
                dummyY = self.fsm.states[node].getYCoord()
                for transition in self.fsm.transitions:
                    if transition.fromState == node:
                        neighbor = transition.toState
                        if layer < len(sortedLayers) - 1 and neighbor in sortedLayers[layer + 1]:
                            neighbourY = self.fsm.states[neighbor].getYCoord()
                            if abs(dummyY - neighbourY) > vertexSeperation:
                            
                                self.fsm.states[neighbor].setYCoord(dummyY)


        if self.hyperparameters['orientation'] == 'vertical':
            
            for state in self.fsm.states.values():
                state.x, state.y = state.y, state.x*-1
  
        






        
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
            return e
        tempPDFPath = os.path.join(mediaFolder, 'temp.pdf')
        if os.path.exists(tempPDFPath):
            subprocess.run(['mv', tempPDFPath, outputFilePath], check=True)
        else:
            print("temp.pdf does not exist")










    def generateTikzCode(self):
        
        
        bend = self.hyperparameters['bend']
        tikzCode = []
        
        
        
        tikzCode.append(r"\documentclass{standalone}")
        tikzCode.append(r"\usepackage{tikz}")
        tikzCode.append(r"\usetikzlibrary{automata,positioning}")  
        tikzCode.append(r"\begin{document}")
        tikzCode.append(r"\begin{tikzpicture}[->,>=stealth,auto,node distance=2.5cm,semithick,every state/.style={minimum width=1cm, minimum height=1cm, text width=0.75cm,align=center}]")


  
        for nodeID, node in self.fsm.states.items():
            x = node.getXCoord()
            y = node.getYCoord()
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
            transitionLabel = longEdge.getLabel()
            sourceLabel = sourceNode.id.lstrip('#')
            endLabel = endNode.id.lstrip('#')
            #if abs(sourceNode.layerValue - endNode.layerValue) == 1:
            #    if sourceNode.layerValue < endNode.layerValue:
            #        tikzCode.append(f"\\draw[->, rounded corners={bend}pt] ({sourceLabel}) to[bend left=30] node[midway, sloped, above] {{{transitionLabel}}} ({endLabel});")
            #    else:
            #        tikzCode.append(f"\\draw[->, rounded corners={bend}pt] ({sourceLabel}) to[bend right=30] node[midway, sloped, above] {{{transitionLabel}}} ({endLabel});")
            #else:

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
            label = transition.getLabel()
            if transition.getIsDummy()== True:
                continue
            elif transition.getIsDummy()== False:
                fromNode = transition.getFrom()
                toNode = transition.getTo()
                fromN = fromNode.lstrip('#')
                toN= toNode.lstrip('#')
                check = False
                for i in self.fsm.transitions:
                    if i.fromState == toNode and i.toState == fromNode:
                        check = True
                        if self.fsm.states[fromNode].layerValue < self.fsm.states[toNode].layerValue:
                            tikzCode.append(f"\\draw[->, rounded corners={bend}pt] ({fromN}) to[bend left=30] node[midway, above, sloped] {{{transitionLabel}}} ({toN});")
                        else:
                            tikzCode.append(f"\\draw[->, rounded corners={bend}pt] ({fromN}) to[bend left=30] node[midway, below, sloped] {{{transitionLabel}}} ({toN});")
                if check == False:
                    tikzCode.append(f"\\path ({fromN}) edge node[midway, sloped, above] {{{label}}} ({toN});")
        
        for transition in self.fsm.selfTransitions:
            fromNode = transition.getFrom().lstrip('#')
            toNode = transition.getTo().lstrip('#')
            label = transition.getLabel()

            if fromNode == toNode:  
                tikzCode.append(f"\\draw[->, loop above] ({fromNode}) to node[sloped, above] {{{label}}} ({toNode});")


        tikzCode.append(r"\end{tikzpicture}")
        tikzCode.append(r"\end{document}")

        return '\n'.join(tikzCode)






    def getNeighboursInPreviousLayer(self,nodeID,layers):
        previousLayer = self.fsm.states[nodeID].layerValue - 1
        potentialNeighbours = layers[previousLayer]
        
        incomingNeighbours = [n for n in potentialNeighbours if any(x.getTo() == nodeID for x in self.fsm.states[n].transitions)]
        outgoingNeighbours = [n for n in potentialNeighbours if any(x.getTo() == n for x in self.fsm.states[nodeID].transitions)]
        
        incomingNeighbours.extend(outgoingNeighbours)
        return incomingNeighbours




    def dfsForSort(self, node, visited, stack):
        visited.add(node)
        for transition in node.transitions:
            neighbourID = transition.getTo()
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
                transLayerVal = self.fsm.states[j.getTo()].layerValue
                if abs(transLayerVal - currLayerVal) > 1 :
                    storeLongEdges.append(j)
        return (storeLongEdges)


    def insertDummyVertices(self, longEdges):
        dummyID = "#0"
        counter = 0
        for edge in longEdges:
            self.fsm.transitions.remove(edge)
            source = edge.fromState
            end = edge.getTo()
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
            if i.getTo() == nodeID:
                predeccessors.append(i.fromState)
        return(predeccessors)
                


