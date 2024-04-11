from .JSONParser import JSONInputParser
from .SugiyamaFramework import SugiyamaFramework
import json


def loadJSON(fileContent):
    return json.loads(fileContent)


def main(fileName, hyperparameters):
    data = loadJSON(fileName)

    parse = JSONInputParser(data)
    
    store = parse.validateJSON()

    if parse.inputValidate == True:
        if parse.checkValidFSM(store):
            
            storeFramework = SugiyamaFramework(store)
        else:
            raise ValueError("Graph is not a valid FSM")
            
    else:
        raise ValueError("Invalid JSON data")
    
    storeFramework.hyperparameters['bend'] = hyperparameters['bend']
    storeFramework.hyperparameters['width'] = hyperparameters['width']
    storeFramework.hyperparameters['height'] = hyperparameters['height']
    storeFramework.hyperparameters['orientation'] = hyperparameters['orientation']
   
    while len(storeFramework.detectCycles()) > 0:
        continue
   
    storelayers = storeFramework.layerAssignment()


    sortedLayers = storeFramework.vertexArrangement(storelayers)
    storeFramework.coordinateAssignment(sortedLayers)
    tikzCode = storeFramework.generateTikzCode()
    storeFramework.compileTikz(tikzCode)
    return tikzCode
