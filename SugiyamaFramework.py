class SugiyamaFramework:
    def __init__(self,FSMData):
        self.fsm = FSMData
        self.feedbackSet = {"lrDir":None, "reverseDir":None}

    def edgeReversal(self):
        pass
    def removeCycles(self):
        visited = {}  # Dictionary to keep track of visited nodes

        def dfs(node, current_path):
            if node in current_path:
                # If the node is already in the current path, a cycle is found
                return True
            if node in visited:
                # If the node has been visited, no need to explore it again
                return False

            visited[node] = True
            current_path.append(node)

            for transition in node.transitions:
                if dfs(transition.toState, current_path):
                    # If a cycle is found deeper in the recursion, return True
                    return True

            current_path.pop()  # Remove the current node from the path
            return False

        # Perform DFS for each node
        for node in self.fsm.states:
            if dfs(node, []):
                return True

        # No cycle found, return False
        return False
    #IMPLEMENT DFS
    def findCycles(self):
        pass