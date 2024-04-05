from .FSMObject import FSMTransition,FSMDummyNode,FSMNode
import os
import copy
import math
import subprocess
import random
import numpy as np
import matplotlib.pyplot as plt
from django.conf import settings
import numpy as np
from scipy.optimize import linprog


class SugiyamaFramework:
    def __init__(self,FSMData):
        self.fsm = FSMData
        self.feedbackSet = []
        self.y_step = 0
        self.hyperparameters = {'repulsionwidth':2, 'width':4,'height':5}


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
        print(self.fsm)
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
       
        toNode.transitions.append(transition)


    def layerAssignment4(self):
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
        barySorted = self.bary(layers)

        return barySorted
    
    def bary(self, layers):
        print(layers)
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
        
        sorted_layers = {}
        for layer, vertices in layers.items():
            sorted_vertices = sorted(vertices, key=lambda vertex: barycenters.get(vertex, 0))
            sorted_layers[layer] = sorted_vertices


        return sorted_layers


 

    

    def dummyArrangement(self):
        storeLong = self.identifyLongEdges()
        
        self.insertDummyVertices(storeLong) 

        layers = {}
        for node_id, node in self.fsm.dummyNodes.items():

            layer_value = node.layerValue
            if layer_value not in layers:
                layers[layer_value] = []

            
            layers[layer_value].append(node_id)

            self.assignXCoords(nodeID=node_id,layer=layer_value)
            


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



    def vertexArrangement(self, sorted_layers):
        vertex_sep = 1
        vertex_sizes = {v: 0.5 for v in self.fsm.states.keys()}
        dummy_vertices = self.fsm.dummyNodes.keys()
        edges = [(i.fromState, i.toState) for i in self.fsm.transitions]

    def vertexArrangement(self, sorted_layers):
        vertex_sep = self.hyperparameters['height']

        # Assign priorities to vertices based on their connectivity and dummy status
        priorities = {}
        for layer, nodes in sorted_layers.items():
            for node in nodes:
                priority = 0
                if node in self.fsm.dummyNodes:
                    priority += 1000  # Give highest priority to dummy vertices
                for transition in self.fsm.transitions:
                    if transition.fromState == node:
                        if layer > 0 and transition.toState in sorted_layers[layer - 1]:
                            priority += 1  # Increase priority based on connections to the previous layer
                priorities[node] = priority

        # Assign y-coordinates to vertices based on their priorities
        for layer, nodes in sorted_layers.items():
            # Sort nodes based on their priorities (higher priority first)
            sorted_nodes = sorted(nodes, key=lambda x: priorities[x], reverse=True)

            # Assign y-coordinates to nodes
            y_coord = 0
            for node in sorted_nodes:
                self.fsm.states[node].y = y_coord
                y_coord += vertex_sep

            # Adjust y-coordinates of lower priority nodes if needed
            for i in range(len(sorted_nodes)):
                node = sorted_nodes[i]
                if node not in self.fsm.dummyNodes:
                    continue
                dummy_y = self.fsm.states[node].y
                for transition in self.fsm.transitions:
                    if transition.fromState == node:
                        neighbor = transition.toState
                        if layer < len(sorted_layers) - 1 and neighbor in sorted_layers[layer + 1]:
                            neighbor_y = self.fsm.states[neighbor].y
                            if abs(dummy_y - neighbor_y) > vertex_sep:
                                # Adjust y-coordinate of the lower priority neighbor
                                self.fsm.states[neighbor].y = dummy_y

        # Find the initial node
        initial_node = self.fsm.initialState

        # Calculate the offset based on the initial node's y-coordinate
        offset = self.fsm.states[initial_node.id].y

        # Adjust the y-coordinates of all vertices by subtracting the offset
        for state in self.fsm.states.values():
            state.y -= offset

  
        






        
    def compile_tikz(self, tikz_code, output_file='output.pdf'):
        media_folder = settings.MEDIA_ROOT
        output_file_path = os.path.join(media_folder, output_file)


        if os.path.exists(output_file_path):
            os.remove(output_file_path)


        temp_tex_path = os.path.join(media_folder, 'temp.tex')
        with open(temp_tex_path, 'w') as f:
            f.write(tikz_code)
        
        try:
            subprocess.run(['pdflatex', '-interaction=nonstopmode', temp_tex_path], check=True, cwd=media_folder)
        except subprocess.CalledProcessError as e:
            print(f"Error compiling TikZ code: {e}")
            return
        temp_pdf_path = os.path.join(media_folder, 'temp.pdf')
        if os.path.exists(temp_pdf_path):
            subprocess.run(['mv', temp_pdf_path, output_file_path], check=True)
            print(f"TikZ code compiled to {output_file}")
        else:
            print("Error: temp.pdf file not generated.")










    def generate_tikz_code(self):
        tikz_code = []
        nodeLabels = [x.strip('#') for x in self.fsm.states.keys()]
        
        
        tikz_code.append(r"\documentclass{standalone}")
        tikz_code.append(r"\usepackage{tikz}")
        tikz_code.append(r"\usetikzlibrary{automata,positioning}")  
        tikz_code.append(r"\begin{document}")
        tikz_code.append(r"\begin{tikzpicture}[->,>=stealth,auto,node distance=2.5cm,semithick,every state/.style={minimum width=1cm, minimum height=1cm, text width=0.75cm,align=center}]")


  
        for node_id, node in self.fsm.states.items():
            x = node.x
            y = node.y
            if type(self.fsm.states[node_id]) is FSMDummyNode:
                continue
            

            if node_id == self.fsm.initialState.id and node in self.fsm.acceptingStates:
                node_id = node_id.lstrip('#')
                tikz_code.append(f"\\node[state, initial, accepting] ({node_id}) at ({x},{y}) {{{node_id}}};")
            elif node_id == self.fsm.initialState.id:
                node_id = node_id.lstrip('#')
                tikz_code.append(f"\\node[state, initial] ({node_id}) at ({x},{y}) {{{node_id}}};")
            elif node in self.fsm.acceptingStates:
                node_id = node_id.lstrip('#')
                tikz_code.append(f"\\node[state, accepting] ({node_id}) at ({x},{y}) {{{node_id}}};")
            else:
                node_id = node_id.lstrip('#')
                tikz_code.append(f"\\node[state] ({node_id}) at ({x},{y}) {{{node_id}}};")

        for long_edge, dummy_nodes in self.fsm.longEdgeMap.items():
            source_node = self.fsm.states[long_edge.fromState]
            target_node = self.fsm.states[long_edge.toState]
            transition_label = long_edge.label[:3]

            if abs(source_node.layerValue - target_node.layerValue) == 1:
                if source_node.layerValue < target_node.layerValue:
                    tikz_code.append(f"\\draw[->, rounded corners=15pt] ({source_node.id.lstrip('#')}) to[bend left=30] node[midway, sloped, above] {{{transition_label}}} ({target_node.id.lstrip('#')});")
                else:
                    tikz_code.append(f"\\draw[->, rounded corners=15pt] ({source_node.id.lstrip('#')}) to[bend right=30] node[midway, sloped, above] {{{transition_label}}} ({target_node.id.lstrip('#')});")
            else:

                if type(source_node) is FSMDummyNode:
                    edge_path = f"({source_node.x},{source_node.y})"
                else:
                    edge_path = f"({source_node.id.lstrip('#')})"

                for dummy_node in dummy_nodes[1:-1]: 
                    edge_path += f" -- ({dummy_node.x},{dummy_node.y})"

                if type(target_node) is FSMDummyNode:
                    edge_path += f" -- ({target_node.x},{target_node.y})"
                else:
                    edge_path += f" -- ({target_node.id.lstrip('#')})"

                
                tikz_code.append(f"\\draw[->, rounded corners=5pt] {edge_path} node[midway, sloped, above] {{{transition_label}}};")

      
        for transition in self.fsm.transitions:
            label = transition.label
            if transition.typeDummy == True:
                continue
            elif transition.typeDummy == False:
                from_node = transition.fromState
                to_node = transition.toState 
                fromNode = self.fsm.states[from_node]
                toNode = self.fsm.states[to_node]

                fromN = transition.fromState.lstrip('#')
                toN= transition.toState.lstrip('#')

                tikz_code.append(f"\\path ({fromN}) edge node[midway, sloped, above] {{{label}}} ({toN});")
        
        for transition in self.fsm.selfTransitions:
            from_node = transition.fromState.lstrip('#')
            to_node = transition.toState.lstrip('#')
            label = transition.label[:3]
            if from_node == to_node:  # Self-transition
                tikz_code.append(f"\\draw[->, loop above] ({from_node}) to node[sloped, above] {{{label}}} ({to_node});")
            else:
                tikz_code.append(f"\\draw[->] ({from_node}) -- node[midway, sloped, above] {{{label}}} ({to_node});")

        tikz_code.append(r"\end{tikzpicture}")
        tikz_code.append(r"\end{document}")

        return '\n'.join(tikz_code)






    #checks for all node types
    def getNeighboursInPreviousLayer3(self,nodeID,layers):
        previousLayer = self.fsm.states[nodeID].layerValue - 1
        potentialNeighbours = layers[previousLayer]
        neighbours = [n for n in potentialNeighbours if any(x.toState == nodeID for x in self.fsm.states[n].transitions)]
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
                




