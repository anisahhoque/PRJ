
import jsonschema 
from .Converter import FSMConverter

class JSONInputParser:
    def __init__(self, inputJSON):
        self.inputJSON = inputJSON
        self.FSMSchema = {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "type": "object",
                            "properties": {
                                "states": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                    "id": {
                                        "type": "string",
                                        "pattern": "^(?!#0).+$","maxLength": 5
                                    }
                                   
                                    },
                                    "required": ["id"]
                                }
                                },
                                "transitions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                    "from": { "type": "string" },
                                    "to": { "type": "string" },
                                    "label": { "type": "string" ,"maxLength": 5},
                                    },
                                    "required": ["from", "to", "label"]
                                }
                                },
                                "initialState": { "type": "string" },
                                "acceptingStates": {
                                "type": "array",
                                "items": { "type": "string" }
                                }
                            },
                            "required": ["states", "transitions", "initialState", "acceptingStates"]
        }
        self.inputValidate = False
        self.validationError = None

    def validateJSON(self):
        try:
            jsonschema.validate(instance=self.inputJSON, schema=self.FSMSchema)
            self.inputValidate = True
            valid = validJSON(self.inputJSON) #store validjson in a seperate object
            storeObject = self.runConversion(valid)
            return storeObject

        except jsonschema.ValidationError as e:
            
            self.inputValidate = False
            self.validationError = str(e)

        except Exception as ex:
            self.inputValidate = False
            self.validationError = str(ex)

    def runConversion(self,validObject):
        converter = FSMConverter()
        newObject = converter.toFSMObject(validObject)
        return newObject
        
    def getValid(self):
        return self.inputValidate

    #postprocessing
    def checkValidFSM(self, FSMObject):
        if FSMObject.getInitial() not in FSMObject.getStates().values():
            return False
        
        if any(item not in FSMObject.getStates().values() for item in FSMObject.getAcceptingStates()):
            return False

        if len(set(FSMObject.getStates().keys())) != len(FSMObject.getStates().keys()):
            return False
        
        for i in FSMObject.getTransitions():
            if i.fromState not in FSMObject.getStates().keys() or i.toState not in FSMObject.getStates().keys():
                return False
            
        for i in FSMObject.getSelfTransitions():
            if i.fromState not in FSMObject.getStates().keys():
                return False
            
        visited = set()
        stack = []
        
      
        start = next(iter(FSMObject.getStates().keys()))
        
        
        stack.append(start)
        
        while stack:
            state = stack.pop()
            if state not in visited:
                visited.add(state)
                for transition in FSMObject.getTransitions():
                    if transition.fromState == state:
                        stack.append(transition.toState)
        
      
        if  len(visited) != len(FSMObject.getStates().keys()):
            
            return False    
        return True

         

class validJSON:
    def __init__(self,validInput):
        self.validJSON = validInput

    def getTransitions(self):
        return self.validJSON["transitions"]
    
    def getInitialState(self):
        return self.validJSON["initialState"]
    
    def getAcceptingStates(self):
        return self.validJSON["acceptingStates"]
    
    def getStates(self):
        return self.validJSON["states"]
    

