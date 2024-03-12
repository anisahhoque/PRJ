import json
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
                                        "pattern": "^#\\d+$" 
                                    },
                                    "name": { "type": "string" } 
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
                                    "label": { "type": "string" },
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
        storeObject = converter.toFSMObject(validObject)
        return storeObject
        
    def getValid(self):
        return self.inputValidate

    def getJSON(self):
        return self.inputJSON
 

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